from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Application(models.Model):
	class Status(models.TextChoices):
		PENDING = "pending", "Pending"
		APPROVED = "approved", "Approved"
		REJECTED = "rejected", "Rejected"

	class BenefitCategory(models.TextChoices):
		NONE = "none", "No benefit"
		DISABILITY = "disability", "Nogironlik"
		IRON_NOTEBOOK = "iron_notebook", "Temir daftar"
		WOMEN_NOTEBOOK = "women_notebook", "Ayollar daftari"
		YOUTH_NOTEBOOK = "youth_notebook", "Yoshlar daftari"

	class PaymentStatus(models.TextChoices):
		UNPAID = "unpaid", "Unpaid"
		PAID = "paid", "Paid"

	student = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="applications",
		limit_choices_to={"role": "student"},
	)
	room = models.ForeignKey(
		"dormitory.Room",
		on_delete=models.PROTECT,
		related_name="applications",
	)
	bed = models.ForeignKey(
		"dormitory.Bed",
		on_delete=models.PROTECT,
		related_name="applications",
	)
	status = models.CharField(
		max_length=20,
		choices=Status.choices,
		default=Status.PENDING,
		db_index=True,
	)
	benefit_category = models.CharField(
		max_length=30,
		choices=BenefitCategory.choices,
		default=BenefitCategory.NONE,
		db_index=True,
	)
	benefit_document = models.FileField(upload_to="benefit_documents/", null=True, blank=True)
	passport_series = models.CharField(max_length=2)
	passport_number = models.CharField(max_length=7)
	passport_pinfl = models.CharField(max_length=14)
	passport_issued_by = models.CharField(max_length=255, blank=True)
	monthly_price = models.PositiveIntegerField(default=300000)
	payment_status = models.CharField(
		max_length=20,
		choices=PaymentStatus.choices,
		default=PaymentStatus.UNPAID,
		db_index=True,
	)
	payment_reference = models.CharField(max_length=100, blank=True)
	paid_at = models.DateTimeField(null=True, blank=True)
	review_comment = models.TextField(blank=True)
	reviewed_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="reviewed_applications",
		limit_choices_to={"role": "staff"},
	)
	reviewed_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True, db_index=True)

	class Meta:
		ordering = ("-created_at",)
		constraints = [
			models.UniqueConstraint(
				fields=["student", "bed", "status"],
				condition=models.Q(status="pending"),
				name="unique_pending_application_per_student_bed",
			),
		]

	def clean(self):
		super().clean()

		if self.student and getattr(self.student, "role", None) != "student":
			raise ValidationError({"student": "Application student must have role=student."})

		if self.reviewed_by and getattr(self.reviewed_by, "role", None) != "staff":
			raise ValidationError({"reviewed_by": "Reviewer must have role=staff."})

		if self.bed_id and self.room_id and self.bed.room_id != self.room_id:
			raise ValidationError({"bed": "Selected bed must belong to the selected room."})

		if self.status in {self.Status.APPROVED, self.Status.REJECTED}:
			if not self.reviewed_by:
				raise ValidationError({"reviewed_by": "Reviewer is required for approved/rejected applications."})
			if not self.reviewed_at:
				self.reviewed_at = timezone.now()
		else:
			if self.reviewed_by or self.reviewed_at:
				raise ValidationError(
					"Review fields are allowed only when application is approved or rejected."
				)

		if self.benefit_category != self.BenefitCategory.NONE and not self.benefit_document:
			raise ValidationError({"benefit_document": "Benefit document is required for selected benefit category."})

		if len((self.passport_series or "").strip()) != 2:
			raise ValidationError({"passport_series": "Passport series must contain 2 letters."})

		if len((self.passport_number or "").strip()) != 7:
			raise ValidationError({"passport_number": "Passport number must contain 7 digits."})

		if len((self.passport_pinfl or "").strip()) != 14:
			raise ValidationError({"passport_pinfl": "PINFL must contain 14 digits."})

	def save(self, *args, **kwargs):
		self.full_clean()
		return super().save(*args, **kwargs)

	def __str__(self) -> str:
		return f"Application #{self.pk or 'new'} - {self.student} - Bed {self.bed.label} - {self.get_status_display()}"
