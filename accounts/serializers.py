from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import StudentProfile

User = get_user_model()


class StudentRegistrationSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
	password_confirm = serializers.CharField(write_only=True, trim_whitespace=False)
	phone = serializers.CharField(max_length=20, write_only=True)
	faculty = serializers.CharField(max_length=255, write_only=True)
	course = serializers.CharField(max_length=100, write_only=True)
	region = serializers.ChoiceField(choices=StudentProfile.Region.choices, write_only=True)

	class Meta:
		model = User
		fields = (
			"id",
			"username",
			"email",
			"password",
			"password_confirm",
			"first_name",
			"last_name",
			"phone",
			"faculty",
			"course",
			"region",
		)
		read_only_fields = ("id",)

	def validate_username(self, value):
		if User.objects.filter(username__iexact=value).exists():
			raise serializers.ValidationError("A user with this username already exists.")
		return value

	def validate_email(self, value):
		if value and User.objects.filter(email__iexact=value).exists():
			raise serializers.ValidationError("A user with this email already exists.")
		return value

	def validate(self, attrs):
		password = attrs.get("password")
		password_confirm = attrs.pop("password_confirm", None)

		if password != password_confirm:
			raise serializers.ValidationError({"password_confirm": "Passwords do not match."})

		candidate_user = User(
			username=attrs.get("username", ""),
			email=attrs.get("email", ""),
			first_name=attrs.get("first_name", ""),
			last_name=attrs.get("last_name", ""),
			role=User.Role.STUDENT,
		)
		validate_password(password, user=candidate_user)
		return attrs

	@transaction.atomic
	def create(self, validated_data):
		profile_data = {
			"first_name": validated_data["first_name"],
			"last_name": validated_data["last_name"],
			"phone": validated_data.pop("phone"),
			"faculty": validated_data.pop("faculty"),
			"course": validated_data.pop("course"),
			"region": validated_data.pop("region"),
		}
		password = validated_data.pop("password")

		user = User.objects.create(
			role=User.Role.STUDENT,
			**validated_data,
		)
		user.set_password(password)
		user.save(update_fields=["password"])

		StudentProfile.objects.create(user=user, **profile_data)
		return user


class LoginUserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ("id", "username", "email", "role", "first_name", "last_name")
		read_only_fields = fields


class LoginResponseSerializer(serializers.Serializer):
	access = serializers.CharField(read_only=True)
	refresh = serializers.CharField(read_only=True, required=False, allow_blank=True)
	user = LoginUserSerializer(read_only=True)


class JWTLoginSerializer(TokenObtainPairSerializer):
	@classmethod
	def get_token(cls, user):
		token = super().get_token(user)
		token["role"] = user.role
		return token

	def validate(self, attrs):
		data = super().validate(attrs)
		data["user"] = LoginUserSerializer(self.user).data
		return data
