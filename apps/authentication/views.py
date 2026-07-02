from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.tenants.models import ( Client, Domain)
from apps.accounts.models import (User,Role)
from .serializers import ( CompanyRegisterSerializer,VerifyPhoneSerializer)

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate,get_user_model
# from django.contrib.auth import (get_user_model)
from rest_framework.permissions import IsAuthenticated

from django_tenants.utils import schema_context

import random

User = get_user_model()

OTP_STORE = {}

class CompanyRegisterAPIView(
    APIView
):
    @transaction.atomic
    def post(
        self,
        request
    ):
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
            data['subdomain']
            .lower()
            .strip()
        )

        if Client.objects.filter(
            schema_name=subdomain
        ).exists():
            return Response(
                {
                    'message':
                    'Subdomain already exists'
                },
                status=400
            )

        Client.objects.create(
            schema_name=subdomain,
            name=data['company_name'],
            phone=data['phone'],
            email=data['email'],
            status='pending',
        )

        return Response(
            {
                'message':
                'Registration submitted successfully. Waiting for admin approval.'
            },
            status=201
        )

# class CompanyRegisterAPIView( APIView):

#     @transaction.atomic
#     def post(self, request):

#         serializer = (
#             CompanyRegisterSerializer(
#                 data=request.data
#             )
#         )

#         serializer.is_valid(
#             raise_exception=True
#         )

#         data = (
#             serializer.validated_data
#         )

#         subdomain = (
#             data["subdomain"]
#             .lower()
#             .strip()
#         )

#         if Client.objects.filter(
#             schema_name=subdomain
#         ).exists():
#             return Response(
#                 {
#                     "message":
#                     "Subdomain already exists"
#                 },
#                 status=400
#             )

#         tenant = Client.objects.create(
#             schema_name=subdomain,
#             name=data["company_name"],
#             phone=data["phone"],
#             email=data["email"],
#         )

#         Domain.objects.create(
#             domain=f"{subdomain}.localhost",
#             tenant=tenant,
#             is_primary=True
#         )

#         user = User.objects.create_user(
#             username=data["admin_name"],
#             email=data["email"],
#             phone=data["phone"],
#             password=data["password"],
#             role=Role.COMPANY_ADMIN,
#         )

#         return Response(
#             {
#                 "message":
#                 "Company registered successfully",

#                 "tenant":
#                 tenant.schema_name,

#                 "domain":
#                 f"{subdomain}.localhost"
#             },
#             status=201
#         )

class LoginAPIView(
    APIView
):
    permission_classes = []

    def post(
        self,
        request
    ):
        email = request.data.get(
            'email'
        )

        password = request.data.get(
            'password'
        )

        user = authenticate(
            request,
            email=email,
            password=password,
        )

        if not user:
            return Response(
                {
                    'error':
                    'Invalid credentials'
                },
                status=401
            )

        refresh = (
            RefreshToken.for_user(
                user
            )
        )

        response = Response({
            'access':
            str(
                refresh.access_token
            ),
            'user': {
                'id': user.id,
                'email': user.email,
                'phone': user.phone,
                'role': user.role,
            },
        })

        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite='Lax',
        )

        return response

# class LoginAPIView(APIView):
#     permission_classes = []

#     def post(self, request):
#         email = request.data.get("email")
#         password = request.data.get("password")

#         user = authenticate(
#             request,
#             email=email,
#             password=password
#         )

#         if not user:
#             return Response(
#                 {"error": "Invalid credentials"},
#                 status=401
#             )

#         refresh = RefreshToken.for_user(user)

#         response = Response({
#             "access": str(refresh.access_token),
#             "user": {
#                 "id": user.id,
#                 "email": user.email,
#                 "role": user.role,
#             }
#         })

#         response.set_cookie(
#             key="refresh_token",
#             value=str(refresh),
#             httponly=True,
#             secure=False,
#             samesite="Lax",
#         )

#         return response
    


# class RefreshAPIView(APIView):
#     permission_classes = []

#     def post(self, request):
#         refresh_token = request.COOKIES.get(
#             "refresh_token"
#         )

#         if not refresh_token:
#             return Response(
#                 {"error": "No refresh token"},
#                 status=401,
#             )

#         try:
#             refresh = RefreshToken(
#                 refresh_token
#             )

#             access = str(
#                 refresh.access_token
#             )

#             return Response({
#                 "access": access
#             })

#         except Exception:
#             return Response(
#                 {"error": "Invalid token"},
#                 status=401,
#             )
        
class RefreshAPIView(
    APIView
):
    permission_classes = []

    def post(
        self,
        request
    ):
        refresh_token = (
            request.COOKIES.get(
                'refresh_token'
            )
        )

        if not refresh_token:
            return Response(
                {
                    'error':
                    'No refresh token'
                },
                status=401
            )

        try:
            refresh = (
                RefreshToken(
                    refresh_token
                )
            )

            access = str(
                refresh.access_token
            )

            return Response({
                'access':
                access
            })

        except Exception:
            return Response(
                {
                    'error':
                    'Invalid token'
                },
                status=401
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
            "phone": user.phone,
            "phone_verified": user.phone_verified,
            "role": user.role,
        })
    
class VerifyPhoneAPIView(
    APIView
):
    def post(
        self,
        request
    ):
        serializer = (
            VerifyPhoneSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        phone = (
            serializer
            .validated_data[
                'phone'
            ]
        )

        otp = (
            serializer
            .validated_data[
                'otp'
            ]
        )

        saved_otp = (
            OTP_STORE.get(
                phone
            )
        )

        if (
            not saved_otp
            or
            saved_otp != otp
        ):
            return Response(
                {
                    'detail':
                    'Invalid OTP'
                },
                status=400
            )

        try:
            user = (
                User.objects.get(
                    phone=phone
                )
            )

        except (
            User.DoesNotExist
        ):
            return Response(
                {
                    'detail':
                    'User not found'
                },
                status=404
            )

        user.phone_verified = True
        user.save()

        OTP_STORE.pop(
            phone,
            None
        )

        return Response({
            'message':
            'Phone verified successfully'
        })
    


class CompanyListAPIView(
    APIView
):
    permission_classes = [
        IsAuthenticated
    ]

    def get(
        self,
        request
    ):
        companies = (
            Client.objects.all()
        )

        data = []

        for company in companies:
            data.append({
                "id":
                company.id,

                "name":
                company.name,

                "schema_name":
                company.schema_name,

                "phone":
                company.phone,

                "status":
                company.status,
            })

        return Response(
            data
        )

class ApproveCompanyAPIView(APIView):
    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request, pk):
        try:
            tenant = Client.objects.get(
                id=pk
            )
        except Client.DoesNotExist:
            return Response(
                {
                    'message':
                    'Company not found'
                },
                status=404
            )

        # Update status
        tenant.status = 'approved'
        tenant.save()

        # Create schema if not exists
        tenant.create_schema(
            check_if_exists=True
        )

        # Create domain
        Domain.objects.get_or_create(
            tenant=tenant,
            domain=f'{tenant.schema_name}.localhost',
            defaults={
                'is_primary': True
            }
        )

        return Response(
            {
                'message':
                'Company approved'
            }
        )
    
# class ApproveCompanyAPIView(APIView):
#     permission_classes = [
#         IsAuthenticated
#     ]

#     def post(self, request, pk):
#         try:
#             tenant = Client.objects.get(
#                 id=pk
#             )
#         except Client.DoesNotExist:
#             return Response(
#                 {
#                     'message':
#                     'Company not found'
#                 },
#                 status=404
#             )

#         tenant.status = 'approved'
#         tenant.auto_create_schema = True
#         tenant.save()

#         Domain.objects.get_or_create(
#             tenant=tenant,
#             domain=f'{tenant.schema_name}.localhost',
#             defaults={
#                 'is_primary': True
#             }
#         )

#         return Response(
#             {
#                 'message':
#                 'Company approved'
#             }
#         )
    
class RejectCompanyAPIView(APIView):
    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request, pk):
        try:
            tenant = Client.objects.get(
                id=pk
            )
        except Client.DoesNotExist:
            return Response(
                {
                    'message':
                    'Company not found'
                },
                status=404
            )

        tenant.status = 'rejected'
        tenant.save()

        return Response(
            {
                'message':
                'Company rejected'
            }
        )