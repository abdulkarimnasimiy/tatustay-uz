from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
	message = "Only students can perform this action."

	def has_permission(self, request, view):
		user = request.user
		return bool(user and user.is_authenticated and getattr(user, "role", None) == "student")

	def has_object_permission(self, request, view, obj):
		user = request.user
		if not user or not user.is_authenticated or getattr(user, "role", None) != "student":
			return False
		return getattr(obj, "student_id", None) == user.id


class IsStaffRole(BasePermission):
	message = "Only staff users can perform this action."

	def has_permission(self, request, view):
		user = request.user
		return bool(user and user.is_authenticated and getattr(user, "role", None) == "staff")

	def has_object_permission(self, request, view, obj):
		user = request.user
		return bool(user and user.is_authenticated and getattr(user, "role", None) == "staff")
