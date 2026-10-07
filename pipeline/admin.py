from django.contrib import admin

from pipeline.models import PipelineRun, RawRecord


class ReadOnlyAdmin(admin.ModelAdmin):
    """Pipeline records are written by the pipeline only."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(PipelineRun)
class PipelineRunAdmin(ReadOnlyAdmin):
    list_display = [
        "started_at",
        "area",
        "status",
        "duration",
        "extracted",
        "rejected",
        "inserted",
        "updated",
        "unchanged",
        "reopened",
        "closed",
    ]
    list_filter = ["status", "area"]


@admin.register(RawRecord)
class RawRecordAdmin(ReadOnlyAdmin):
    list_display = ["__str__", "run", "fetched_at"]
    list_filter = ["run__area"]
    search_fields = ["osm_id"]
    list_select_related = ["run__area"]
