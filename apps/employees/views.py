from django.db import transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.tenants.models import UserTenant
from apps.employees.models import Employee, Invitation, Role
from apps.employees.serializers import (
    InvitationSerializer,
    AcceptInvitationSerializer,
    EmployeeSerializer,
    EmployeeUpdateSerializer,
)
from apps.employees.services import (
    create_employee_invitation,
    accept_employee_invitation,
)


def is_workspace_admin(request):
    """
    Helper to check if the current user is a superuser or a COMPANY_ADMIN
    in the active tenant workspace.
    """
    if request.user.is_superuser:
        return True

    tenant = getattr(request, "tenant", None)
    if not tenant:
        return False

    sender_employee = Employee.objects.filter(tenant=tenant, user=request.user).first()
    return sender_employee is not None and sender_employee.role == Role.COMPANY_ADMIN



# 1. INVITATIONS MANAGEMENT

class InviteEmployeeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tenant = getattr(request, "tenant", None)
        if not tenant:
            return Response(
                {"error": "Tenant context not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not is_workspace_admin(request):
            return Response(
                {"error": "Permission denied. Only Company Admins can invite employees."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = InvitationSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        invited_by = Employee.objects.filter(tenant=tenant, user=request.user).first()

        invitation = create_employee_invitation(
            tenant=tenant,
            invited_by=invited_by,
            full_name=data["full_name"],
            email=data["email"],
            phone=data["phone"],
            role=data["role"],
        )

        return Response(
            {
                "message": "Invitation sent successfully.",
                "invitation": InvitationSerializer(invitation).data,
            },
            status=status.HTTP_201_CREATED,
        )


class AcceptInvitationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AcceptInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        employee = accept_employee_invitation(
            token=data["token"],
            password=data["password"],
        )

        return Response(
            {
                "message": "Invitation accepted. Profile created successfully.",
                "employee": EmployeeSerializer(employee).data,
            },
            status=status.HTTP_200_OK,
        )


# 2. EMPLOYEE CRUD & PROFILES

class EmployeeListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = getattr(request, "tenant", None)
        if not tenant:
            return Response(
                {"error": "Tenant context not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ensure the user belongs to this tenant
        if not request.user.is_superuser:
            belongs = Employee.objects.filter(tenant=tenant, user=request.user).exists()
            if not belongs:
                return Response(
                    {"error": "Access denied. You do not belong to this workspace."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        employees = Employee.objects.filter(tenant=tenant).order_by("-created_at")
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EmployeeDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, tenant):
        try:
            return Employee.objects.get(id=pk, tenant=tenant)
        except Employee.DoesNotExist:
            return None

    def get(self, request, pk):
        tenant = getattr(request, "tenant", None)
        employee = self.get_object(pk, tenant)
        if not employee:
            return Response(
                {"error": "Employee profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EmployeeSerializer(employee)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        tenant = getattr(request, "tenant", None)
        employee = self.get_object(pk, tenant)
        if not employee:
            return Response(
                {"error": "Employee profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only allow updates if the user is a Company Admin or updating their own profile
        is_self = employee.user == request.user
        if not is_self and not is_workspace_admin(request):
            return Response(
                {"error": "Permission denied. You can only update your own profile."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = EmployeeUpdateSerializer(employee, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Re-fetch with full details
        full_serializer = EmployeeSerializer(employee)
        return Response(full_serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        return self.patch(request, pk)

    @transaction.atomic
    def delete(self, request, pk):
        tenant = getattr(request, "tenant", None)
        employee = self.get_object(pk, tenant)
        if not employee:
            return Response(
                {"error": "Employee profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not is_workspace_admin(request):
            return Response(
                {"error": "Permission denied. Only Company Admins can remove employees."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Break the schema association (UserTenant) and delete profile
        UserTenant.objects.filter(user=employee.user, tenant=tenant).delete()
        employee.delete()

        return Response(
            {"message": "Employee profile removed and workspace unmapped successfully."},
            status=status.HTTP_200_OK,
        )


# 3. BLOCK / UNBLOCK EMPLOYEE

class BlockEmployeeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        tenant = getattr(request, "tenant", None)
        if not is_workspace_admin(request):
            return Response(
                {"error": "Permission denied. Only Company Admins can block employees."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            employee = Employee.objects.get(id=pk, tenant=tenant)
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if employee.is_blocked:
            return Response(
                {"message": "Employee is already blocked."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        employee.is_blocked = True
        employee.is_active = False
        employee.save(update_fields=["is_blocked", "is_active"])

        return Response(
            {"message": "Employee blocked successfully."},
            status=status.HTTP_200_OK,
        )


class UnblockEmployeeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        tenant = getattr(request, "tenant", None)
        if not is_workspace_admin(request):
            return Response(
                {"error": "Permission denied. Only Company Admins can unblock employees."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            employee = Employee.objects.get(id=pk, tenant=tenant)
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not employee.is_blocked:
            return Response(
                {"message": "Employee is already active."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        employee.is_blocked = False
        employee.is_active = True
        employee.save(update_fields=["is_blocked", "is_active"])

        return Response(
            {"message": "Employee unblocked successfully."},
            status=status.HTTP_200_OK,
        )
