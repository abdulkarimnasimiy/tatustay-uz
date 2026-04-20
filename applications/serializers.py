from django.utils import timezone
from rest_framework import serializers

from .models import Application


class ApplicationCreateSerializer(serializers.ModelSerializer):
	passport_series = serializers.CharField(max_length=2)
	passport_number = serializers.CharField(max_length=7)
	passport_pinfl = serializers.CharField(max_length=14)
	passport_issued_by = serializers.CharField(max_length=255, required=False, allow_blank=True)
	benefit_document = serializers.FileField(required=False, allow_null=True)

	class Meta:
		model = Application
		fields = (
			"id",
			"room",
			"bed",
			"benefit_category",
			"benefit_document",
			"passport_series",
			"passport_number",
			"passport_pinfl",
			"passport_issued_by",
			"monthly_price",
			"payment_status",
			"status",
			"created_at",
		)
		read_only_fields = ("id", "status", "created_at", "monthly_price", "payment_status")

	def validate(self, attrs):
		request = self.context.get("request")
		student = getattr(request, "user", None)

		if not student or not student.is_authenticated:
			raise serializers.ValidationError("Authentication is required.")
		if student.role != "student":
			raise serializers.ValidationError("Only students can submit applications.")

		room = attrs.get("room")
		bed = attrs.get("bed")
		if bed and room and bed.room_id != room.id:
			raise serializers.ValidationError({"bed": "Selected bed must belong to the selected room."})

		if bed and bed.is_occupied:
			raise serializers.ValidationError({"bed": "This bed is already occupied."})

		benefit_category = attrs.get("benefit_category", Application.BenefitCategory.NONE)
		benefit_document = attrs.get("benefit_document")
		if benefit_category != Application.BenefitCategory.NONE and not benefit_document:
			raise serializers.ValidationError({"benefit_document": "Imtiyoz uchun hujjat fayli majburiy."})

		if room:
			is_disability = benefit_category == Application.BenefitCategory.DISABILITY
			if is_disability and room.floor.number != 2:
				raise serializers.ValidationError({
					"room": "Nogironlik imtiyozidagi talabalar uchun faqat 2-qavatdan joy tanlanadi."
				})
			if not is_disability and room.floor.number == 2:
				raise serializers.ValidationError({
					"room": "2-qavat faqat nogironlik imtiyozi bor talabalar uchun ajratilgan."
				})

		attrs["passport_series"] = attrs["passport_series"].upper()

		has_active_for_bed = Application.objects.filter(
			student=student,
			bed=bed,
			status__in=[Application.Status.PENDING, Application.Status.APPROVED],
		).exists()
		if has_active_for_bed:
			raise serializers.ValidationError(
				{"bed": "You already have an active pending/approved application for this bed."}
			)

		return attrs

	def create(self, validated_data):
		validated_data["student"] = self.context["request"].user
		validated_data["status"] = Application.Status.PENDING
		validated_data["reviewed_by"] = None
		validated_data["reviewed_at"] = None
		validated_data["review_comment"] = ""
		validated_data["monthly_price"] = 300000
		validated_data["payment_status"] = Application.PaymentStatus.UNPAID
		return super().create(validated_data)


class StudentApplicationListSerializer(serializers.ModelSerializer):
	student_username = serializers.CharField(source="student.username", read_only=True)
	student_full_name = serializers.SerializerMethodField()
	student_phone = serializers.SerializerMethodField()
	student_faculty = serializers.SerializerMethodField()
	student_course = serializers.SerializerMethodField()
	student_region = serializers.SerializerMethodField()
	student_distance_km = serializers.SerializerMethodField()
	student_distance_level = serializers.SerializerMethodField()
	room_number = serializers.CharField(source="room.number", read_only=True)
	floor_number = serializers.IntegerField(source="room.floor.number", read_only=True)
	bed_label = serializers.CharField(source="bed.label", read_only=True)
	benefit_document = serializers.FileField(read_only=True)
	reviewed_by_username = serializers.CharField(source="reviewed_by.username", read_only=True)
	reviewed_by_full_name = serializers.SerializerMethodField()
	workflow_step = serializers.SerializerMethodField()
	workflow_total_steps = serializers.SerializerMethodField()
	workflow_label = serializers.SerializerMethodField()

	def _profile(self, obj):
		return getattr(obj.student, "student_profile", None)

	def get_student_full_name(self, obj):
		profile = self._profile(obj)
		if profile:
			return f"{profile.first_name} {profile.last_name}".strip()
		return (obj.student.get_full_name() or "").strip() or obj.student.username

	def get_student_phone(self, obj):
		profile = self._profile(obj)
		return profile.phone if profile else ""

	def get_student_faculty(self, obj):
		profile = self._profile(obj)
		return profile.faculty if profile else ""

	def get_student_course(self, obj):
		profile = self._profile(obj)
		return profile.course if profile else ""

	def get_student_region(self, obj):
		profile = self._profile(obj)
		return profile.get_region_display() if profile else ""

	def get_student_distance_km(self, obj):
		profile = self._profile(obj)
		return profile.distance_km if profile else None

	def get_student_distance_level(self, obj):
		profile = self._profile(obj)
		return profile.get_distance_level_display() if profile else ""

	def get_reviewed_by_full_name(self, obj):
		reviewer = getattr(obj, "reviewed_by", None)
		if not reviewer:
			return ""
		return (reviewer.get_full_name() or "").strip() or reviewer.username

	def get_workflow_step(self, obj):
		if obj.status == Application.Status.APPROVED:
			if obj.payment_status == Application.PaymentStatus.PAID:
				return 4
			return 3
		return 2

	def get_workflow_total_steps(self, obj):
		return 4

	def get_workflow_label(self, obj):
		if obj.status == Application.Status.REJECTED:
			return "Ariza ko'rib chiqildi va rad etildi"
		if obj.status == Application.Status.PENDING:
			return "Ariza yuborilgan, xodim ko'rib chiqmoqda"
		if obj.status == Application.Status.APPROVED and obj.payment_status != Application.PaymentStatus.PAID:
			return "Ariza tasdiqlangan, to'lov kutilmoqda"
		return "Rasmiylashtirish yakunlandi, to'lov tasdiqlandi"

	class Meta:
		model = Application
		fields = (
			"id",
			"student_username",
			"student_full_name",
			"student_phone",
			"student_faculty",
			"student_course",
			"student_region",
			"student_distance_km",
			"student_distance_level",
			"status",
			"benefit_category",
			"benefit_document",
			"passport_series",
			"passport_number",
			"passport_pinfl",
			"passport_issued_by",
			"monthly_price",
			"payment_status",
			"payment_reference",
			"paid_at",
			"created_at",
			"reviewed_at",
			"reviewed_by_username",
			"reviewed_by_full_name",
			"review_comment",
			"room",
			"room_number",
			"floor_number",
			"bed",
			"bed_label",
			"workflow_step",
			"workflow_total_steps",
			"workflow_label",
		)
		read_only_fields = fields


class StaffApplicationReviewSerializer(serializers.ModelSerializer):
	status = serializers.ChoiceField(choices=[Application.Status.APPROVED, Application.Status.REJECTED])
	review_comment = serializers.CharField(required=False, allow_blank=True, allow_null=False)

	class Meta:
		model = Application
		fields = ("status", "review_comment")

	def validate(self, attrs):
		request = self.context.get("request")
		reviewer = getattr(request, "user", None)
		if not reviewer or not reviewer.is_authenticated:
			raise serializers.ValidationError("Authentication is required.")
		if reviewer.role != "staff":
			raise serializers.ValidationError("Only staff can review applications.")

		instance = self.instance
		if not instance:
			raise serializers.ValidationError("Application instance is required for review.")
		if instance.status != Application.Status.PENDING:
			raise serializers.ValidationError("Only pending applications can be reviewed.")

		new_status = attrs.get("status")
		if new_status == Application.Status.APPROVED and instance.bed.is_occupied:
			raise serializers.ValidationError({"status": "Cannot approve because the bed is already occupied."})

		return attrs

	def update(self, instance, validated_data):
		instance.status = validated_data["status"]
		instance.review_comment = validated_data.get("review_comment", "")
		instance.reviewed_by = self.context["request"].user
		instance.reviewed_at = timezone.now()
		instance.save(update_fields=["status", "review_comment", "reviewed_by", "reviewed_at"])
		return instance


class StudentApplicationPaymentSerializer(serializers.ModelSerializer):
	payment_reference = serializers.CharField(required=False, allow_blank=True)

	class Meta:
		model = Application
		fields = ("payment_reference",)
