from rest_framework import serializers

from .models import Bed, Floor, Room


class FloorSerializer(serializers.ModelSerializer):
	class Meta:
		model = Floor
		fields = ("id", "number")
		read_only_fields = fields


class RoomSerializer(serializers.ModelSerializer):
	floor_number = serializers.IntegerField(source="floor.number", read_only=True)
	capacity = serializers.SerializerMethodField()
	available_beds = serializers.SerializerMethodField()
	room_type = serializers.SerializerMethodField()

	def get_capacity(self, obj):
		return obj.beds.count()

	def get_available_beds(self, obj):
		return obj.beds.filter(is_occupied=False).count()

	def get_room_type(self, obj):
		return "6 kishilik" if obj.beds.count() == 6 else "3 kishilik"

	class Meta:
		model = Room
		fields = ("id", "number", "floor", "floor_number", "capacity", "available_beds", "room_type")
		read_only_fields = fields


class BedSerializer(serializers.ModelSerializer):
	room_number = serializers.CharField(source="room.number", read_only=True)
	floor_number = serializers.IntegerField(source="room.floor.number", read_only=True)

	class Meta:
		model = Bed
		fields = ("id", "label", "is_occupied", "room", "room_number", "floor_number")
		read_only_fields = fields
