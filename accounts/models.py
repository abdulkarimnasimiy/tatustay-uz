from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


REGION_DISTANCE_KM = {
	"tashkent_city": 0,
	"tashkent_region": 30,
	"sirdaryo": 110,
	"jizzakh": 200,
	"namangan": 300,
	"andijan": 350,
	"fargona": 320,
	"samarkand": 310,
	"navoi": 430,
	"bukhara": 560,
	"qashqadaryo": 520,
	"surxondaryo": 640,
	"khorezm": 980,
	"republic_of_karakalpakstan": 1100,
}


def get_distance_level(distance_km: int) -> str:
	if distance_km <= 150:
		return "near"
	if distance_km <= 400:
		return "medium"
	if distance_km <= 700:
		return "far"
	return "very_far"


class User(AbstractUser):
	class Role(models.TextChoices):
		STUDENT = "student", "Student"
		STAFF = "staff", "Staff"

	role = models.CharField(
		max_length=20,
		choices=Role.choices,
		default=Role.STUDENT,
		db_index=True,
	)

	@property
	def is_student(self) -> bool:
		return self.role == self.Role.STUDENT

	@property
	def is_staff_user(self) -> bool:
		return self.role == self.Role.STAFF


class StudentProfile(models.Model):
	class Region(models.TextChoices):
		TASHKENT_CITY = "tashkent_city", "Toshkent shahri"
		TASHKENT_REGION = "tashkent_region", "Toshkent viloyati"
		SIRDARYO = "sirdaryo", "Sirdaryo"
		JIZZAKH = "jizzakh", "Jizzax"
		NAMANGAN = "namangan", "Namangan"
		ANDIJAN = "andijan", "Andijon"
		FARGONA = "fargona", "Farg'ona"
		SAMARKAND = "samarkand", "Samarqand"
		NAVOI = "navoi", "Navoiy"
		BUKHARA = "bukhara", "Buxoro"
		QASHQADARYO = "qashqadaryo", "Qashqadaryo"
		SURXONDARYO = "surxondaryo", "Surxondaryo"
		KHOREZM = "khorezm", "Xorazm"
		REPUBLIC_OF_KARAKALPAKSTAN = "republic_of_karakalpakstan", "Qoraqalpog'iston Respublikasi"

	class DistanceLevel(models.TextChoices):
		NEAR = "near", "Yaqin"
		MEDIUM = "medium", "O'rtacha"
		FAR = "far", "Uzoq"
		VERY_FAR = "very_far", "Juda uzoq"

	user = models.OneToOneField(
		User,
		on_delete=models.CASCADE,
		related_name="student_profile",
	)
	first_name = models.CharField(max_length=150)
	last_name = models.CharField(max_length=150)
	phone = models.CharField(max_length=20)
	faculty = models.CharField(max_length=255)
	course = models.CharField(max_length=100)
	region = models.CharField(max_length=40, choices=Region.choices, default=Region.TASHKENT_CITY)
	distance_km = models.PositiveSmallIntegerField(default=0)
	distance_level = models.CharField(max_length=20, choices=DistanceLevel.choices, default=DistanceLevel.NEAR)

	def clean(self):
		super().clean()
		if self.user and not self.user.is_student:
			raise ValidationError({"user": "Student profile can only be created for users with role=student."})

	def save(self, *args, **kwargs):
		self.distance_km = REGION_DISTANCE_KM.get(self.region, 0)
		self.distance_level = get_distance_level(self.distance_km)
		self.full_clean()
		return super().save(*args, **kwargs)

	def __str__(self) -> str:
		return f"{self.user.username} - {self.faculty}"
