from django.core.mail import send_mail

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Client
from .serializers import CompanySerializer

from apps.accounts.models import Role


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

        send_mail(
            subject="TrackFlow Workspace Approved",
            message=f"""
Hello {company.name},

Congratulations!

Your TrackFlow AI workspace has been approved.

You can now login using your registered account.

Thank you,
TrackFlow AI Team
""",
            from_email=None,
            recipient_list=[company.email],
            fail_silently=False,
        )

        return Response(
            {
                "message": "Company approved successfully"
            },
            status=200
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

        except Client.DoesNotExist:
            return Response(
                {
                    "message": "Company not found"
                },
                status=404
            )

        company.status = "rejected"
        company.save()

        send_mail(
            subject="TrackFlow Workspace Rejected",
            message=f"""
Hello {company.name},

Unfortunately, your TrackFlow AI workspace request has been rejected.

If you believe this was a mistake, please contact our support team.

Thank you,
TrackFlow AI Team
""",
            from_email=None,
            recipient_list=[company.email],
            fail_silently=False,
        )

        return Response(
            {
                "message": "Company rejected successfully"
            },
            status=200
        )
  