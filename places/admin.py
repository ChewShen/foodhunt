from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from places.models import Area, Place


@admin.register(Area)
class AreaAdmin(GISModelAdmin):
    list_display = ["name", "slug", "radius_m", "is_active"]
    list_filter = ["is_active"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Place)
class PlaceAdmin(GISModelAdmin):
    list_display = ["name", "area", "cuisine_list", "is_open", "last_seen_at"]
    list_filter = ["area", ("closed_at", admin.EmptyFieldListFilter)]
    search_fields = ["name", "brand", "address"]
    readonly_fields = [
        "osm_type",
        "osm_id",
        "content_hash",
        "first_seen_at",
        "last_seen_at",
        "updated_at",
        "closed_at",
    ]

    @admin.display(description="Cuisines")
    def cuisine_list(self, obj):
        return ", ".join(obj.cuisines)

    @admin.display(boolean=True, description="Open")
    def is_open(self, obj):
        return obj.is_open
