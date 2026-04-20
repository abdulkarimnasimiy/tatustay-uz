from django.db import transaction
from django.db.models import Case, Count, IntegerField, Q, Value, When
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import parsers
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Application
from .permissions import IsStaffRole, IsStudent
from .serializers import (
	ApplicationCreateSerializer,
	StudentApplicationPaymentSerializer,
	StaffApplicationReviewSerializer,
	StudentApplicationListSerializer,
)


class StudentApplicationCreateAPIView(CreateAPIView):
	serializer_class = ApplicationCreateSerializer
	permission_classes = [IsStudent]
	parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]


class StudentMyApplicationListAPIView(ListAPIView):
	serializer_class = StudentApplicationListSerializer
	permission_classes = [IsStudent]

	def get_queryset(self):
		return (
			Application.objects.filter(student=self.request.user)
			.select_related("room", "room__floor", "bed")
			.order_by("-created_at")
		)


class StudentApplicationPayAPIView(APIView):
	permission_classes = [IsStudent]

	@transaction.atomic
	def post(self, request, application_id):
		application = get_object_or_404(
			Application.objects.select_for_update().select_related("student"),
			pk=application_id,
			student=request.user,
		)

		if application.status != Application.Status.APPROVED:
			return Response(
				{"detail": "Faqat tasdiqlangan arizalar uchun to'lov qilish mumkin."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		if application.payment_status == Application.PaymentStatus.PAID:
			return Response(
				{"detail": "Bu ariza uchun to'lov allaqachon amalga oshirilgan."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		serializer = StudentApplicationPaymentSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		payment_reference = serializer.validated_data.get("payment_reference") or f"PAY-{application.id}-{int(timezone.now().timestamp())}"

		application.payment_status = Application.PaymentStatus.PAID
		application.payment_reference = payment_reference
		application.paid_at = timezone.now()
		application.save(update_fields=["payment_status", "payment_reference", "paid_at"])

		return Response(StudentApplicationListSerializer(application).data, status=status.HTTP_200_OK)


class StaffPendingApplicationListAPIView(ListAPIView):
	serializer_class = StudentApplicationListSerializer
	permission_classes = [IsStaffRole]

	def get_queryset(self):
		return (
			Application.objects.filter(status=Application.Status.PENDING)
			.select_related("student", "student__student_profile", "room", "room__floor", "bed")
			.annotate(
				disability_priority=Case(
					When(benefit_category=Application.BenefitCategory.DISABILITY, then=Value(0)),
					default=Value(1),
					output_field=IntegerField(),
				)
			)
			.order_by("disability_priority", "created_at")
		)


class StaffApproveApplicationAPIView(APIView):
	permission_classes = [IsStaffRole]

	@transaction.atomic
	def post(self, request, application_id):
		application = get_object_or_404(
			Application.objects.select_for_update().select_related("bed"),
			pk=application_id,
		)

		if application.status != Application.Status.PENDING:
			return Response(
				{"detail": "Only pending applications can be approved."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		bed = application.bed
		bed = bed.__class__.objects.select_for_update().get(pk=bed.pk)
		if bed.is_occupied:
			return Response(
				{"detail": "Cannot approve because this bed is already occupied."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		floor_number = application.room.floor.number
		is_disability = application.benefit_category == Application.BenefitCategory.DISABILITY
		if is_disability and floor_number != 2:
			return Response(
				{"detail": "Nogironlik toifasidagi arizalar faqat 2-qavatdan tasdiqlanadi."},
				status=status.HTTP_400_BAD_REQUEST,
			)
		if not is_disability and floor_number == 2:
			return Response(
				{"detail": "2-qavat faqat nogironlik toifasidagi talabalar uchun."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		serializer = StaffApplicationReviewSerializer(
			instance=application,
			data={"status": Application.Status.APPROVED, "review_comment": request.data.get("review_comment", "")},
			partial=True,
			context={"request": request},
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		bed.is_occupied = True
		bed.save(update_fields=["is_occupied"])

		return Response(StudentApplicationListSerializer(application).data, status=status.HTTP_200_OK)


class StaffRoomAvailabilityAPIView(APIView):
	permission_classes = [IsStaffRole]

	def get(self, request):
		from dormitory.models import Room

		rooms = (
			Room.objects.select_related("floor")
			.annotate(
				total_beds=Count("beds"),
				available_beds=Count("beds", filter=Q(beds__is_occupied=False)),
			)
			.filter(available_beds__gt=0)
			.order_by("floor__number", "number")
		)

		floors_map = {}
		total_available_beds = 0
		for room in rooms:
			floor_no = room.floor.number
			total_available_beds += room.available_beds
			if floor_no not in floors_map:
				floors_map[floor_no] = {
					"floor_number": floor_no,
					"available_beds": 0,
					"rooms": [],
				}

			floors_map[floor_no]["available_beds"] += room.available_beds
			floors_map[floor_no]["rooms"].append(
				{
					"room_id": room.id,
					"room_number": room.number,
					"available_beds": room.available_beds,
					"total_beds": room.total_beds,
				}
			)

		data = {
			"total_available_beds": total_available_beds,
			"total_rooms_with_availability": rooms.count(),
			"floors": sorted(floors_map.values(), key=lambda item: item["floor_number"]),
		}
		return Response(data, status=status.HTTP_200_OK)


class StaffApprovedByRoomAPIView(APIView):
	permission_classes = [IsStaffRole]

	def get(self, request):
		approved_apps = (
			Application.objects.filter(status=Application.Status.APPROVED)
			.select_related("student", "student__student_profile", "room", "room__floor", "bed", "reviewed_by")
			.order_by("room__floor__number", "room__number", "reviewed_at")
		)

		rooms_map = {}
		for app in approved_apps:
			room_key = f"{app.room.floor.number}:{app.room.number}"
			if room_key not in rooms_map:
				rooms_map[room_key] = {
					"floor_number": app.room.floor.number,
					"room_id": app.room.id,
					"room_number": app.room.number,
					"approved_count": 0,
					"students": [],
				}

			serialized = StudentApplicationListSerializer(app).data
			rooms_map[room_key]["approved_count"] += 1
			rooms_map[room_key]["students"].append(
				{
					"application_id": serialized["id"],
					"student_username": serialized["student_username"],
					"student_full_name": serialized["student_full_name"],
					"bed_label": serialized["bed_label"],
					"payment_status": serialized["payment_status"],
					"reviewed_at": serialized["reviewed_at"],
					"reviewed_by_username": serialized["reviewed_by_username"],
					"reviewed_by_full_name": serialized["reviewed_by_full_name"],
				}
			)

		data = sorted(
			rooms_map.values(),
			key=lambda item: (item["floor_number"], item["room_number"]),
		)
		return Response(data, status=status.HTTP_200_OK)


class StaffRejectApplicationAPIView(APIView):
	permission_classes = [IsStaffRole]

	@transaction.atomic
	def post(self, request, application_id):
		application = get_object_or_404(
			Application.objects.select_for_update().select_related("bed"),
			pk=application_id,
		)

		if application.status != Application.Status.PENDING:
			return Response(
				{"detail": "Only pending applications can be rejected."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		serializer = StaffApplicationReviewSerializer(
			instance=application,
			data={"status": Application.Status.REJECTED, "review_comment": request.data.get("review_comment", "")},
			partial=True,
			context={"request": request},
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response(StudentApplicationListSerializer(application).data, status=status.HTTP_200_OK)
