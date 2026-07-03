from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.tenants.models import ( Client, Domain)
from apps.accounts.models import (User,Role)
from .serializers import ( CompanyRegisterSerializer,VerifyPhoneSerializer)
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate,get_user_model
from rest_framework.permissions import IsAuthenticated
from django_tenants.utils import schema_context
import random

import pyotp
import qrcode
import base64
from io import BytesIO

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

class LoginAPIView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(
            request,
            email=email,
            password=password,
        )

        if not user:
            return Response(
                {
                    'error': 'Invalid credentials'
                },
                status=401
            )

        # MFA enabled admin
        if (
            user.is_mfa_enabled
            and user.role in [
                Role.SUPER_ADMIN,
                Role.COMPANY_ADMIN,
            ]
        ):
            return Response({
                'mfa_required': True,
                'email': user.email,
            })

        # Normal login
        refresh = RefreshToken.for_user(user)

        response = Response({
            'access': str(
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


class MFALoginAPIView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        try:
            user = User.objects.get(
                email=email
            )

        except User.DoesNotExist:
            return Response(
                {
                    'error': 'User not found'
                },
                status=404
            )

        if not user.is_mfa_enabled:
            return Response(
                {
                    'error': 'MFA not enabled'
                },
                status=400
            )

        totp = pyotp.TOTP(
            user.mfa_secret
        )

        if not totp.verify(code):
            return Response(
                {
                    'error': 'Invalid code'
                },
                status=400
            )

        refresh = RefreshToken.for_user(
            user
        )

        response = Response({
            'access': str(
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
    
class MFASetupAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not user.mfa_secret:
            user.mfa_secret = pyotp.random_base32()
            user.save()

        totp = pyotp.TOTP(user.mfa_secret)

        uri = totp.provisioning_uri(
            name=user.email,
            issuer_name='TrackFlow AI'
        )

        qr = qrcode.make(uri)

        buffer = BytesIO()
        qr.save(buffer, format='PNG')

        qr_code = base64.b64encode(
            buffer.getvalue()
        ).decode()

        return Response({
            'secret': user.mfa_secret,
            'qr': qr_code,
        })
    
class MFAVerifyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get('code')
        user = request.user

        if not user.mfa_secret:
            return Response(
                {'message': 'MFA not setup'},
                status=400
            )

        totp = pyotp.TOTP(user.mfa_secret)

        if not totp.verify(code):
            return Response(
                {'message': 'Invalid code'},
                status=400
            )

        user.is_mfa_enabled = True
        user.save()

        return Response({
            'message': 'MFA enabled successfully'
        })