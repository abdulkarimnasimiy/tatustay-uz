from django.urls import path

from .views import (
	StaffApproveApplicationAPIView,
	StaffApprovedByRoomAPIView,
	StaffRoomAvailabilityAPIView,
	StaffPendingApplicationListAPIView,
	StaffRejectApplicationAPIView,
	StudentApplicationCreateAPIView,
	StudentApplicationPayAPIView,
	StudentMyApplicationListAPIView,
)


urlpatterns = [
	path("student/applications/", StudentApplicationCreateAPIView.as_view(), name="student-application-create"),
	path("student/applications/<int:application_id>/pay/", StudentApplicationPayAPIView.as_view(), name="student-application-pay"),
	path("student/my-applications/", StudentMyApplicationListAPIView.as_view(), name="student-my-applications"),
	path("staff/applications/pending/", StaffPendingApplicationListAPIView.as_view(), name="staff-pending-applications"),
	path("staff/applications/approved-by-room/", StaffApprovedByRoomAPIView.as_view(), name="staff-approved-by-room"),
	path("staff/availability/", StaffRoomAvailabilityAPIView.as_view(), name="staff-room-availability"),
	path("staff/applications/<int:application_id>/approve/", StaffApproveApplicationAPIView.as_view(), name="staff-approve-application"),
	path("staff/applications/<int:application_id>/reject/", StaffRejectApplicationAPIView.as_view(), name="staff-reject-application"),
]
