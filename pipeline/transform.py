"""Turn raw Overpass elements into clean place records.

Everything here is pure: no database, no network, no clock. That keeps the
rules easy to test and lets past runs be replayed from stored raw data.
"""

import hashlib
import json
import re
from dataclasses import asdict, dataclass

OSM_TYPES = {"node", "way", "relation"}
ADDRESS_KEYS = ("addr:housenumber", "addr:street", "addr:postcode", "addr:city")


@dataclass(frozen=True)
class CleanPlace:
    osm_type: str
    osm_id: int
    name: str
    lat: float
    lon: float
    cuisines: tuple[str, ...] = ()
    brand: str = ""
    address: str = ""
    phone: str = ""
    website: str = ""
    opening_hours: str = ""

    @property
    def key(self):
        return (self.osm_type, self.osm_id)

    def content_hash(self):
        data = asdict(self)
        data["cuisines"] = list(self.cuisines)
        encoded = json.dumps(data, sort_keys=True, ensure_ascii=False).encode()
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class Rejection:
    osm_type: str
    osm_id: int | None
    reason: str


def element_key(element):
    """(osm_type, osm_id) for a raw element, or None if it has no usable identity."""
    osm_type, osm_id = element.get("type"), element.get("id")
    if osm_type not in OSM_TYPES or not isinstance(osm_id, int):
        return None
    return osm_type, osm_id


def transform(element):
    """Return a CleanPlace, or a Rejection explaining why the element can't be used."""
    key = element_key(element)
    if key is None:
        return Rejection(str(element.get("type", "")), element.get("id"), "invalid_identity")
    osm_type, osm_id = key

    tags = element.get("tags") or {}
    name = _text(tags.get("name")) or _text(tags.get("name:en"))
    if not name:
        return Rejection(osm_type, osm_id, "missing_name")

    coordinates = _coordinates(element)
    if coordinates is None:
        return Rejection(osm_type, osm_id, "missing_coordinates")
    lat, lon = coordinates

    return CleanPlace(
        osm_type=osm_type,
        osm_id=osm_id,
        name=name,
        lat=lat,
        lon=lon,
        cuisines=split_cuisines(tags.get("cuisine")),
        brand=_text(tags.get("brand")),
        address=format_address(tags),
        phone=_text(tags.get("phone")) or _text(tags.get("contact:phone")),
        website=_text(tags.get("website")) or _text(tags.get("contact:website")),
        opening_hours=_text(tags.get("opening_hours")),
    )


def split_cuisines(value):
    """'Chinese;dim sum, Noodle' -> ('chinese', 'dim_sum', 'noodle')."""
    if not value:
        return ()
    seen = []
    for part in re.split(r"[;,]", value):
        cuisine = re.sub(r"\s+", "_", part.strip().lower())
        if cuisine and cuisine not in seen:
            seen.append(cuisine)
    return tuple(seen)


def format_address(tags):
    parts = [_text(tags.get(key)) for key in ADDRESS_KEYS]
    return ", ".join(part for part in parts if part)


def _coordinates(element):
    # Nodes carry lat/lon directly; ways and relations carry a center from `out center`.
    source = element if "lat" in element else element.get("center") or {}
    lat, lon = source.get("lat"), source.get("lon")
    if not isinstance(lat, int | float) or not isinstance(lon, int | float):
        return None
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    return float(lat), float(lon)


def _text(value):
    return " ".join(value.split()) if isinstance(value, str) else ""
