import copy
import json
from pathlib import Path

import pytest

from pipeline.models import PipelineRun, RawRecord
from pipeline.runner import run_area
from places.models import Area, Place

FIXTURE = Path(__file__).parent / "fixtures" / "overpass_ss15.json"

pytestmark = pytest.mark.django_db


@pytest.fixture
def elements():
    return json.loads(FIXTURE.read_text())["elements"]


@pytest.fixture
def ss15():
    return Area.objects.get(slug="ss15")


def counts(run):
    fields = ["extracted", "rejected", "inserted", "updated", "unchanged", "reopened", "closed"]
    return {field: getattr(run, field) for field in fields}


def without(elements, osm_id):
    return [e for e in elements if e["id"] != osm_id]


def test_seeded_areas_exist():
    assert set(Area.objects.values_list("slug", flat=True)) == {"ss15", "mid-valley", "cyberjaya"}


def test_first_run_loads_valid_places(ss15, elements):
    run = run_area(ss15, elements)

    assert run.status == PipelineRun.Status.SUCCEEDED
    assert run.finished_at is not None
    # 7 elements, one duplicate: 6 unique, of which 2 are rejected.
    assert counts(run) == {
        "extracted": 6,
        "rejected": 2,
        "inserted": 4,
        "updated": 0,
        "unchanged": 0,
        "reopened": 0,
        "closed": 0,
    }
    assert RawRecord.objects.filter(run=run).count() == 6


def test_chain_branches_in_one_area_are_kept_apart(ss15, elements):
    run_area(ss15, elements)

    assert Place.objects.filter(name="Burger Barn").count() == 2


def test_clean_fields_are_stored(ss15, elements):
    run_area(ss15, elements)

    place = Place.objects.get(osm_type="node", osm_id=9000000003)
    assert place.name == "Restoran Kopi Dim Sum"
    assert place.cuisines == ["chinese", "dim_sum", "noodle"]
    assert place.address == "12, Jalan SS 15/8, 47500, Subang Jaya"
    assert place.phone == "+60 3-5600 0000"
    assert (place.location.x, place.location.y) == (101.5887, 3.0749)
    assert place.area == ss15


def test_rerunning_the_same_data_changes_nothing(ss15, elements):
    run_area(ss15, elements)
    before = {p.pk: (p.content_hash, p.updated_at) for p in Place.objects.all()}

    run = run_area(ss15, elements)

    assert counts(run)["unchanged"] == 4
    assert counts(run)["inserted"] == counts(run)["updated"] == counts(run)["closed"] == 0
    assert {p.pk: (p.content_hash, p.updated_at) for p in Place.objects.all()} == before
    assert all(p.last_seen_at == run.started_at for p in Place.objects.all())


def test_changed_place_is_updated(ss15, elements):
    run_area(ss15, elements)
    changed = copy.deepcopy(elements)
    # The fixture repeats this element; deduplication keeps the last copy, so change them all.
    for element in changed:
        if element["id"] == 9000000001:
            element["tags"]["cuisine"] = "burger;chicken"

    run = run_area(ss15, changed)

    assert (run.updated, run.unchanged) == (1, 3)
    place = Place.objects.get(osm_id=9000000001)
    assert place.cuisines == ["burger", "chicken"]
    assert place.updated_at == run.started_at


def test_missing_place_is_closed_then_reopened(ss15, elements):
    run_area(ss15, elements)

    run = run_area(ss15, without(elements, 9000000002))
    place = Place.objects.get(osm_id=9000000002)
    assert run.closed == 1
    assert place.closed_at == run.started_at
    assert not place.is_open

    run = run_area(ss15, elements)
    place.refresh_from_db()
    assert (run.reopened, run.closed) == (1, 0)
    assert place.is_open


def test_closing_only_affects_the_runs_area(ss15, elements):
    run_area(ss15, elements)
    cyberjaya = Area.objects.get(slug="cyberjaya")
    other = {"type": "node", "id": 1, "lat": 2.92, "lon": 101.65, "tags": {"name": "Cafe"}}

    run = run_area(cyberjaya, [other])

    assert run.closed == 0
    assert Place.objects.filter(area=ss15, closed_at__isnull=True).count() == 4


def test_empty_extract_closes_nothing(ss15, elements):
    run_area(ss15, elements)

    run = run_area(ss15, [])

    assert run.status == PipelineRun.Status.SUCCEEDED
    assert run.closed == 0
    assert not Place.objects.filter(closed_at__isnull=False).exists()


def test_failed_run_is_recorded_and_rolled_back(ss15, elements, monkeypatch):
    def explode(*args, **kwargs):
        raise RuntimeError("database went away")

    monkeypatch.setattr("pipeline.runner.load_places", explode)

    with pytest.raises(RuntimeError):
        run_area(ss15, elements)

    run = PipelineRun.objects.get()
    assert run.status == PipelineRun.Status.FAILED
    assert run.error == "RuntimeError: database went away"
    assert run.finished_at is not None
    assert not RawRecord.objects.exists()
    assert not Place.objects.exists()
