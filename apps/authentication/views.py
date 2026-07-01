from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.tenants.models import ( Client, Domain)
from apps.accounts.models import (User,Role)
from .serializers import ( CompanyRegisterSerializer)

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated


class CompanyRegisterAPIView( APIView):

    @transaction.atomic
    def post(self, request):

        serializer = (
            CompanyRegisterSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = (
            serializer.validated_data
        )

        subdomain = (
            data["subdomain"]
            .lower()
            .strip()
        )

        if Client.objects.filter(
            schema_name=subdomain
        ).exists():
            return Response(
                {
                    "message":
                    "Subdomain already exists"
                },
                status=400
            )

        tenant = Client.objects.create(
            schema_name=subdomain,
            name=data["company_name"],
            phone=data["phone"],
            email=data["email"],
        )

        Domain.objects.create(
            domain=f"{subdomain}.localhost",
            tenant=tenant,
            is_primary=True
        )

        user = User.objects.create_user(
            username=data["admin_name"],
            email=data["email"],
            phone=data["phone"],
            password=data["password"],
            role=Role.COMPANY_ADMIN,
        )

        return Response(
            {
                "message":
                "Company registered successfully",

                "tenant":
                tenant.schema_name,

                "domain":
                f"{subdomain}.localhost"
            },
            status=201
        )



class LoginAPIView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(
            request,
            email=email,
            password=password
        )

        if not user:
            return Response(
                {"error": "Invalid credentials"},
                status=401
            )

        refresh = RefreshToken.for_user(user)

        response = Response({
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
            }
        })

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite="Lax",
        )

        return response
    


class RefreshAPIView(APIView):
    permission_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get(
            "refresh_token"
        )

        if not refresh_token:
            return Response(
                {"error": "No refresh token"},
                status=401,
            )

        try:
            refresh = RefreshToken(
                refresh_token
            )

            access = str(
                refresh.access_token
            )

            return Response({
                "access": access
            })

        except Exception:
            return Response(
                {"error": "Invalid token"},
                status=401,
            )
        



class LogoutAPIView(APIView):
    def post(self, request):
        response = Response({
            "message": "Logged out"
        })

        response.delete_cookie(
            "refresh_token"
        )

        return response
    
class MeAPIView(APIView):
    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):
        user = request.user

        return Response({
            "id": user.id,
            "email": user.email,
            "role": user.role,
        })