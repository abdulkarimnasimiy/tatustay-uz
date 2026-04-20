from django.urls import path

from .views import BedByRoomListAPIView, FloorListAPIView, RoomByFloorListAPIView


urlpatterns = [
	path("floors/", FloorListAPIView.as_view(), name="floor-list"),
	path("floors/<int:floor_id>/rooms/", RoomByFloorListAPIView.as_view(), name="room-list-by-floor"),
	path("rooms/<int:room_id>/beds/", BedByRoomListAPIView.as_view(), name="bed-list-by-room"),
]
