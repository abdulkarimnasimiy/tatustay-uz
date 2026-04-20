from rest_framework import permissions
from rest_framework.generics import ListAPIView

from .models import Bed, Floor, Room
from .serializers import BedSerializer, FloorSerializer, RoomSerializer


class FloorListAPIView(ListAPIView):
	queryset = Floor.objects.all()
	serializer_class = FloorSerializer
	permission_classes = [permissions.IsAuthenticated]


class RoomByFloorListAPIView(ListAPIView):
	serializer_class = RoomSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		floor_id = self.kwargs["floor_id"]
		return Room.objects.filter(floor_id=floor_id).select_related("floor")


class BedByRoomListAPIView(ListAPIView):
	serializer_class = BedSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		room_id = self.kwargs["room_id"]
		return Bed.objects.filter(room_id=room_id).select_related("room", "room__floor")
