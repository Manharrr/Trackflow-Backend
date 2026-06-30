from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.tenants.models import (
    Client,
    Domain
)

from apps.accounts.models import (
    User,
    Role
)

from .serializers import (
    CompanyRegisterSerializer
)


class CompanyRegisterAPIView(
    APIView
):

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
