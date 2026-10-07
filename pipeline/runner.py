"""Run the pipeline for one area: store raw elements, transform them, load places."""

import logging
from dataclasses import dataclass

from django.contrib.gis.geos import Point
from django.db import transaction
from django.utils import timezone

from pipeline.models import PipelineRun, RawRecord
from pipeline.transform import CleanPlace, element_key, transform
from places.models import Place

logger = logging.getLogger(__name__)

PLACE_FIELDS = (
    "name",
    "location",
    "cuisines",
    "brand",
    "address",
    "phone",
    "website",
    "opening_hours",
    "content_hash",
)


@dataclass
class LoadStats:
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0
    reopened: int = 0
    closed: int = 0


def run_area(area, elements):
    """Run the pipeline for `area` over already-extracted Overpass `elements`.

    The run row is committed before any work starts, so a failure is recorded
    as a failed run instead of vanishing with the rolled-back transaction.
    """
    run = PipelineRun.objects.create(area=area)
    try:
        with transaction.atomic():
            elements = dedupe_elements(elements)
            store_raw(run, elements)

            places, rejected = [], 0
            for element in elements:
                result = transform(element)
                if isinstance(result, CleanPlace):
                    places.append(result)
                else:
                    rejected += 1
                    logger.info("Rejected %s/%s: %s", result.osm_type, result.osm_id, result.reason)

            stats = load_places(area, places, now=run.started_at)
    except Exception as exc:
        run.status = PipelineRun.Status.FAILED
        run.error = f"{type(exc).__name__}: {exc}"
        run.finished_at = timezone.now()
        run.save()
        logger.exception("Pipeline run %s for %s failed", run.pk, area.slug)
        raise

    run.status = PipelineRun.Status.SUCCEEDED
    run.extracted = len(elements)
    run.rejected = rejected
    run.inserted = stats.inserted
    run.updated = stats.updated
    run.unchanged = stats.unchanged
    run.reopened = stats.reopened
    run.closed = stats.closed
    run.finished_at = timezone.now()
    run.save()
    logger.info(
        "Run %s for %s: %s extracted, %s rejected, %s inserted, %s updated, "
        "%s unchanged, %s reopened, %s closed",
        run.pk,
        area.slug,
        run.extracted,
        run.rejected,
        run.inserted,
        run.updated,
        run.unchanged,
        run.reopened,
        run.closed,
    )
    return run


def dedupe_elements(elements):
    """Keep the last copy of each OSM element; drop elements with no identity."""
    by_key = {}
    for element in elements:
        key = element_key(element)
        if key is not None:
            by_key[key] = element
    return list(by_key.values())


def store_raw(run, elements):
    RawRecord.objects.bulk_create(
        RawRecord(run=run, osm_type=e["type"], osm_id=e["id"], payload=e, fetched_at=run.started_at)
        for e in elements
    )


def load_places(area, places, now):
    """Upsert `places` into `area`, keyed on OSM element, and close the ones not seen.

    Areas are assumed not to overlap: a place belongs to the area that last
    reported it, and only that area's runs can close it.
    """
    stats = LoadStats()
    incoming = {place.key: place for place in places}
    existing = {
        (p.osm_type, p.osm_id): p
        for p in Place.objects.filter(
            osm_type__in={k[0] for k in incoming}, osm_id__in={k[1] for k in incoming}
        )
    }

    to_create, to_change, unchanged_pks = [], [], []
    for key, clean in incoming.items():
        content_hash = clean.content_hash()
        place = existing.get(key)

        if place is None:
            to_create.append(
                Place(
                    osm_type=clean.osm_type,
                    osm_id=clean.osm_id,
                    area=area,
                    first_seen_at=now,
                    last_seen_at=now,
                    updated_at=now,
                    **_place_values(clean, content_hash),
                )
            )
            stats.inserted += 1
            continue

        is_closed = place.closed_at is not None
        if not is_closed and place.content_hash == content_hash and place.area_id == area.pk:
            unchanged_pks.append(place.pk)
            stats.unchanged += 1
            continue

        if is_closed:
            stats.reopened += 1
        else:
            stats.updated += 1
        for field, value in _place_values(clean, content_hash).items():
            setattr(place, field, value)
        place.area = area
        place.last_seen_at = now
        place.updated_at = now
        place.closed_at = None
        to_change.append(place)

    created = Place.objects.bulk_create(to_create)
    Place.objects.bulk_update(
        to_change, [*PLACE_FIELDS, "area", "last_seen_at", "updated_at", "closed_at"]
    )
    Place.objects.filter(pk__in=unchanged_pks).update(last_seen_at=now)

    # An empty extract almost always means a bad response, not every restaurant closing.
    if incoming:
        seen_pks = [p.pk for p in created] + [p.pk for p in to_change] + unchanged_pks
        stats.closed = (
            Place.objects.filter(area=area, closed_at__isnull=True)
            .exclude(pk__in=seen_pks)
            .update(closed_at=now, updated_at=now)
        )

    return stats


def _place_values(clean, content_hash):
    return {
        "name": clean.name,
        "location": Point(clean.lon, clean.lat, srid=4326),
        "cuisines": list(clean.cuisines),
        "brand": clean.brand,
        "address": clean.address,
        "phone": clean.phone,
        "website": clean.website,
        "opening_hours": clean.opening_hours,
        "content_hash": content_hash,
    }
