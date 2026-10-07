from django.contrib.gis.geos import Point
from django.db import migrations

# Centres and radii carried over from the 1.x fetch_shops command.
AREAS = [
    ("ss15", "SS15", 3.0751, 101.5891, 1000),
    ("mid-valley", "Mid Valley", 3.1176, 101.6776, 1500),
    ("cyberjaya", "Cyberjaya", 2.9213, 101.6559, 3000),
]


def seed_areas(apps, schema_editor):
    Area = apps.get_model("places", "Area")
    for slug, name, lat, lon, radius_m in AREAS:
        Area.objects.get_or_create(
            slug=slug,
            defaults={
                "name": name,
                "center": Point(lon, lat, srid=4326),
                "radius_m": radius_m,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("places", "0001_initial"),
    ]

    operations = [
        # Reversing leaves the areas in place: places and runs may reference them.
        migrations.RunPython(seed_areas, migrations.RunPython.noop),
    ]
