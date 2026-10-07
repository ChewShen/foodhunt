from pipeline.transform import CleanPlace, Rejection, split_cuisines, transform


def node(**tags):
    return {"type": "node", "id": 1, "lat": 3.07, "lon": 101.59, "tags": tags}


def test_node_becomes_clean_place():
    place = transform(
        node(
            name="Kopi House",
            brand="Kopi Co",
            cuisine="coffee_shop",
            phone="+60 3-1234 5678",
            website="https://example.com",
            opening_hours="Mo-Fr 08:00-17:00",
            **{
                "addr:housenumber": "12",
                "addr:street": "Jalan SS 15/8",
                "addr:city": "Subang Jaya",
            },
        )
    )

    assert place == CleanPlace(
        osm_type="node",
        osm_id=1,
        name="Kopi House",
        lat=3.07,
        lon=101.59,
        cuisines=("coffee_shop",),
        brand="Kopi Co",
        address="12, Jalan SS 15/8, Subang Jaya",
        phone="+60 3-1234 5678",
        website="https://example.com",
        opening_hours="Mo-Fr 08:00-17:00",
    )


def test_way_uses_center_coordinates():
    place = transform(
        {"type": "way", "id": 7, "center": {"lat": 3.1, "lon": 101.6}, "tags": {"name": "Hall"}}
    )

    assert (place.osm_type, place.osm_id, place.lat, place.lon) == ("way", 7, 3.1, 101.6)


def test_name_falls_back_to_english_name():
    assert transform(node(**{"name:en": "Banana Leaf House"})).name == "Banana Leaf House"


def test_whitespace_is_collapsed():
    assert transform(node(name="  Restoran   Kopi ")).name == "Restoran Kopi"


def test_contact_tags_are_fallbacks():
    place = transform(
        node(name="X", **{"contact:phone": "+60 1", "contact:website": "https://x.example"})
    )

    assert (place.phone, place.website) == ("+60 1", "https://x.example")


def test_missing_name_is_rejected():
    assert transform(node(cuisine="malay")) == Rejection("node", 1, "missing_name")


def test_missing_coordinates_are_rejected():
    result = transform({"type": "way", "id": 7, "tags": {"name": "No Centre"}})

    assert result == Rejection("way", 7, "missing_coordinates")


def test_out_of_range_coordinates_are_rejected():
    element = {"type": "node", "id": 1, "lat": 95, "lon": 101.5, "tags": {"name": "X"}}

    assert transform(element).reason == "missing_coordinates"


def test_unknown_element_type_is_rejected():
    assert transform({"type": "area", "id": 1}).reason == "invalid_identity"


def test_split_cuisines_normalises_and_dedupes():
    assert split_cuisines("Chinese;dim sum, Noodle;chinese") == ("chinese", "dim_sum", "noodle")
    assert split_cuisines(None) == ()
    assert split_cuisines(" ; ") == ()


def test_content_hash_is_stable_and_tracks_changes():
    first = transform(node(name="Kopi House", cuisine="coffee_shop"))
    same = transform(node(name="Kopi House", cuisine="coffee_shop"))
    renamed = transform(node(name="Kopi House 2", cuisine="coffee_shop"))

    assert first.content_hash() == same.content_hash()
    assert first.content_hash() != renamed.content_hash()
