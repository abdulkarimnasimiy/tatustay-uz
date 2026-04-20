from django.urls import path

from .views import JWTLoginAPIView, StudentRegistrationAPIView


urlpatterns = [
	path("register/", StudentRegistrationAPIView.as_view(), name="student-register"),
	path("login/", JWTLoginAPIView.as_view(), name="jwt-login"),
]
