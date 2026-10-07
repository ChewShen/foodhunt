from django.db import models
from django.utils import timezone

from places.models import Area


class PipelineRun(models.Model):
    """One extract → transform → load pass over a single area."""

    class Status(models.TextChoices):
        RUNNING = "running"
        SUCCEEDED = "succeeded"
        FAILED = "failed"

    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="runs")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.RUNNING)
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)
    error = models.TextField(blank=True)

    extracted = models.PositiveIntegerField(default=0)
    rejected = models.PositiveIntegerField(default=0)
    inserted = models.PositiveIntegerField(default=0)
    updated = models.PositiveIntegerField(default=0)
    unchanged = models.PositiveIntegerField(default=0)
    reopened = models.PositiveIntegerField(default=0)
    closed = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.area} @ {self.started_at:%Y-%m-%d %H:%M} ({self.status})"

    @property
    def duration(self):
        if self.finished_at is None:
            return None
        return self.finished_at - self.started_at


class RawRecord(models.Model):
    """An OpenStreetMap element exactly as the extractor received it."""

    run = models.ForeignKey(PipelineRun, on_delete=models.CASCADE, related_name="raw_records")
    osm_type = models.CharField(max_length=8)
    osm_id = models.BigIntegerField()
    payload = models.JSONField()
    fetched_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["run", "osm_type", "osm_id"], name="unique_raw_record_per_run"
            ),
        ]

    def __str__(self):
        return f"{self.osm_type}/{self.osm_id}"
