from django.core.mail import send_mail

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Client,Domain
from .serializers import CompanySerializer

from apps.accounts.models import Role


from .services import ( send_company_approved_email,send_company_rejected_email,)

class CompanyListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role != Role.SUPER_ADMIN:
            return Response(
                {
                    "message": "Permission denied"
                },
                status=403
            )

        companies = Client.objects.exclude(
            schema_name="public"
        )

        serializer = CompanySerializer(
            companies,
            many=True
        )

        return Response(serializer.data)


class PendingCompanyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role != Role.SUPER_ADMIN:
            return Response(
                {
                    "message": "Permission denied"
                },
                status=403
            )

        companies = Client.objects.filter(
            status="pending"
        )

        serializer = CompanySerializer(
            companies,
            many=True
        )

        return Response(serializer.data)
    


class ApproveCompanyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):

        if request.user.role != Role.SUPER_ADMIN:
            return Response(
                {
                    "message": "Permission denied"
                },
                status=403
            )

        try:
            company = Client.objects.get(id=pk)

        except Client.DoesNotExist:
            return Response(
                {
                    "message": "Company not found"
                },
                status=404
            )

        company.status = "approved"
        company.save()
        
        # Create PostgreSQL schema
        company.create_schema(
        check_if_exists=True)

        # Create domain
        Domain.objects.get_or_create(
            domain=f"{company.schema_name}.localhost",
            tenant=company,
            is_primary=True,
            )

        send_company_approved_email(company)

        return Response(
            {"message": "Company approved successfully"},status=200
        )

       

class RejectCompanyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):

        if request.user.role != Role.SUPER_ADMIN:
            return Response(
                {
                    "message": "Permission denied"
                },
                status=403
            )

        try:
            company = Client.objects.get(id=pk)

            reason=request.data.get("reason")

            if not reason:
                return Response({"message":"reason required"},status=400)


        except Client.DoesNotExist:
            return Response(
                {
                    "message": "Company not found"
                },
                status=404
            )

        company.status = "rejected"
        company.rejection_reason=reason
        company.save()


        send_company_rejected_email(company,reason)

        return Response({
            "message": "Company rejected successfully"
        },status=200)

class CompanyDetailAPIView(
    APIView
):
    permission_classes = [
        IsAuthenticated
    ]

    def get(
        self,
        request,
        pk,
    ):
        try:

            company = (
                Client.objects.get(
                    pk=pk
                )
            )

        except Client.DoesNotExist:

            return Response(
                {
                    "error":
                    "Company not found"
                },
                status=404
            )

        serializer = (
            CompanySerializer(
                company
            )
        )

        return Response(
            serializer.data
        )   


from django.db.models import Count


class SuperAdminDashboardAPIView(
    APIView
):
    permission_classes = [
        IsAuthenticated
    ]

    def get(
        self,
        request,
    ):

        total = Client.objects.count()

        pending = Client.objects.filter(
            status="pending"
        ).count()

        approved = Client.objects.filter(
            status="approved"
        ).count()

        rejected = Client.objects.filter(
            status="rejected"
        ).count()

        recent = (
            Client.objects
            .order_by(
                "-created_at"
            )[:5]
        )

        return Response(
            {
                "summary": {
                    "total": total,
                    "pending": pending,
                    "approved": approved,
                    "rejected": rejected,
                },
                "recent": CompanySerializer(
                    recent,
                    many=True,
                ).data,
            }
        )
  