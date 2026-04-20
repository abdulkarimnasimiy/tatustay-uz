from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import JWTLoginSerializer, StudentRegistrationSerializer


class StudentRegistrationAPIView(CreateAPIView):
	serializer_class = StudentRegistrationSerializer
	permission_classes = [permissions.AllowAny]


class JWTLoginAPIView(TokenObtainPairView):
	serializer_class = JWTLoginSerializer
	permission_classes = [permissions.AllowAny]

	def post(self, request, *args, **kwargs):
		response = super().post(request, *args, **kwargs)
		return Response(response.data, status=status.HTTP_200_OK)
