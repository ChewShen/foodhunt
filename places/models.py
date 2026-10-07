from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField


class Area(models.Model):
    """A circular region the pipeline collects restaurants for."""

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    center = models.PointField(geography=True)
    radius_m = models.PositiveIntegerField(help_text="Search radius in metres.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Place(models.Model):
    """A restaurant, keyed by its OpenStreetMap element."""

    class OsmType(models.TextChoices):
        NODE = "node"
        WAY = "way"
        RELATION = "relation"

    osm_type = models.CharField(max_length=8, choices=OsmType.choices)
    osm_id = models.BigIntegerField()
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="places")

    name = models.TextField()
    location = models.PointField(geography=True)
    cuisines = ArrayField(models.TextField(), default=list, blank=True)
    brand = models.TextField(blank=True)
    address = models.TextField(blank=True)
    phone = models.TextField(blank=True)
    website = models.TextField(blank=True)
    opening_hours = models.TextField(blank=True)

    # Hash of the clean fields above, so loads can skip rows that haven't changed.
    content_hash = models.CharField(max_length=64)
    first_seen_at = models.DateTimeField()
    last_seen_at = models.DateTimeField()
    updated_at = models.DateTimeField(help_text="When the pipeline last changed this place.")
    closed_at = models.DateTimeField(
        null=True, blank=True, help_text="Set when the place disappears from OpenStreetMap."
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["osm_type", "osm_id"], name="unique_osm_element"),
        ]
        indexes = [models.Index(fields=["area", "closed_at"])]

    def __str__(self):
        return self.name

    @property
    def is_open(self):
        return self.closed_at is None
