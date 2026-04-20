from django.contrib import admin
 
from .models import Bed, Floor, Room


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
	list_display = ("id", "number")
	ordering = ("number",)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
	list_display = ("id", "number", "floor")
	list_filter = ("floor",)
	search_fields = ("number",)
	ordering = ("floor__number", "number")


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
	list_display = ("id", "label", "room", "is_occupied")
	list_filter = ("is_occupied", "room__floor")
	search_fields = ("label", "room__number")
	ordering = ("room__floor__number", "room__number", "label")
