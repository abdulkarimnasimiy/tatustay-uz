from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import StudentProfile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
	fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("role",)}),)
	list_display = ("username", "email", "first_name", "last_name", "role", "is_active", "is_staff")
	list_filter = UserAdmin.list_filter + ("role",)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "first_name", "last_name", "phone", "faculty", "course")
	search_fields = ("user__username", "first_name", "last_name", "faculty", "course")
