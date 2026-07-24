from django.db import transaction
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Client, Domain, UserTenant
from .serializers import CompanySerializer
from .services import (
    send_company_approved_email,
    send_company_rejected_email,
)


class CompanyListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser:
            return Response(
                {"message": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )

        companies = Client.objects.exclude(schema_name="public")
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PendingCompanyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser:
            return Response(
                {"message": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )

        companies = Client.objects.filter(status="pending")
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ApproveCompanyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def patch(self, request, pk):
        if not request.user.is_superuser:
            return Response(
                {"message": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            company = Client.objects.get(id=pk)
        except Client.DoesNotExist:
            return Response(
                {"message": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if company.status == "approved":
            return Response(
                {"message": "Company is already approved."},
                status=status.HTTP_400_BAD_REQUEST
            )

        company.status = "approved"
        company.save()

        # Create PostgreSQL schema
        company.create_schema(check_if_exists=True)
        
        from django.conf import settings
        # Create domain
        # domain_name = f"{company.schema_name}.trackflow.local"
        domain_name = (
            f"{company.schema_name}.{settings.BASE_DOMAIN}"
        )
        Domain.objects.get_or_create(
            domain=domain_name,
            tenant=company,
            defaults={"is_primary": True},
        )

        # Look up User and map Tenant / Admin Employee profiles
        from apps.accounts.models import User
        user = User.objects.filter(email=company.email).first()

        if user:
            # Create UserTenant relation
            UserTenant.objects.get_or_create(
                user=user,
                tenant=company,
                defaults={"is_active": True},
            )

            # Switch context to the company schema to create the Employee record inside it
            from django_tenants.utils import schema_context
            with schema_context(company.schema_name):
                from apps.employees.models.employee import Employee, Role
                Employee.objects.get_or_create(
                    tenant=company,
                    user=user,
                    defaults={
                        "role": Role.COMPANY_ADMIN,
                        "full_name": user.first_name or user.username or "Company Admin",
                        "email": user.email,
                        "phone": user.phone,
                        "is_active": True,
                        "is_blocked": False,
                    },
                )

        # Send approval notification email
        send_company_approved_email(company)

        return Response(
            {"message": "Company approved successfully and tenant resources created."},
            status=status.HTTP_200_OK,
        )


class RejectCompanyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def patch(self, request, pk):
        if not request.user.is_superuser:
            return Response(
                {"message": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            company = Client.objects.get(id=pk)
        except Client.DoesNotExist:
            return Response(
                {"message": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        reason = request.data.get("reason")
        if not reason:
            return Response(
                {"message": "Reason is required to reject a workspace request."},
                status=status.HTTP_400_BAD_REQUEST
            )

        company.status = "rejected"
        company.rejection_reason = reason
        company.save()

        # Send rejection notification email
        send_company_rejected_email(company, reason)

        return Response(
            {"message": "Company rejected successfully."},
            status=status.HTTP_200_OK,
        )


class CompanyDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            company = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return Response(
                {"error": "Company not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CompanySerializer(company)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        try:
            company = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return Response(
                {"error": "Company not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Allow Super Admin or mapped UserTenant company admin to update details
        if not request.user.is_superuser:
            user_tenant_exists = UserTenant.objects.filter(user=request.user, tenant=company).exists()
            if not user_tenant_exists:
                return Response(
                    {"error": "Permission denied"},
                    status=status.HTTP_403_FORBIDDEN
                )

        name = request.data.get("name")
        if name:
            company.name = name

        address = request.data.get("address")
        if address is not None:
            company.address = address

        description = request.data.get("description")
        if description is not None:
            company.description = description

        logo = request.FILES.get("logo")
        if logo:
            company.logo = logo

        company.save()
        serializer = CompanySerializer(company)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SuperAdminDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser:
            return Response(
                {"message": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )

        total = Client.objects.exclude(schema_name="public").count()
        pending = Client.objects.filter(status="pending").count()
        approved = Client.objects.filter(status="approved").count()
        rejected = Client.objects.filter(status="rejected").count()

        recent = Client.objects.exclude(schema_name="public").order_by("-created_at")[:5]

        return Response(
            {
                "summary": {
                    "total": total,
                    "pending": pending,
                    "approved": approved,
                    "rejected": rejected,
                },
                "recent": CompanySerializer(recent, many=True).data,
            },
            status=status.HTTP_200_OK,
        )