from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.employees.models.employee import Employee, Role
from apps.employees.serializers.employee_serializers import (
    EmployeeCreateSerializer,
    EmployeeListSerializer,
    EmployeeDetailSerializer,
    EmployeeUpdateSerializer,
)

from apps.employees.services.onboarding_service import EmployeeOnboardingService
from apps.employees.services.employee_service import EmployeeService
from apps.employees.permissions.employee_permissions import (
    IsCompanyAdmin,
    IsCompanyAdminOrOperationsManager,
    IsTenantEmployee,
)


class EmployeeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdmin]

    def post(self, request):
        serializer = EmployeeCreateSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        employee = EmployeeOnboardingService.create_employee(
            tenant=request.tenant,
            **serializer.validated_data
        )

        return Response(
            {
                "message": "Employee created successfully.",
                "data": EmployeeDetailSerializer(employee).data,
            },
            status=status.HTTP_201_CREATED,
        )


class EmployeeListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrOperationsManager]

    def get(self, request):
        employees = EmployeeService.list_employees(request.tenant)

        serializer = EmployeeListSerializer(
            employees,
            many=True,
        )

        return Response(serializer.data)


class EmployeeDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTenantEmployee]

    def get(self, request, employee_id):
        employee = EmployeeService.get_employee(
            employee_id=employee_id,
            tenant=request.tenant,
        )

        # Allow if the user is a Company Admin, Operations Manager, or viewing their own profile
        is_self = employee.user == request.user
        has_privileged_role = Employee.objects.filter(
            user=request.user,
            tenant=request.tenant,
            role__in=[Role.COMPANY_ADMIN, Role.OPERATIONS_MANAGER]
        ).exists() or request.user.is_superuser

        if not is_self and not has_privileged_role:
            return Response(
                {"detail": "You do not have permission to view this employee profile."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = EmployeeDetailSerializer(employee)

        return Response(serializer.data)


class EmployeeUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTenantEmployee]

    def patch(self, request, employee_id):
        employee = EmployeeService.get_employee(
            employee_id=employee_id,
            tenant=request.tenant,
        )

        # Allow updates if the user is a Company Admin or updating their own profile
        is_self = employee.user == request.user
        is_admin = Employee.objects.filter(
            user=request.user,
            tenant=request.tenant,
            role=Role.COMPANY_ADMIN
        ).exists() or request.user.is_superuser

        if not is_self and not is_admin:
            return Response(
                {"detail": "Permission denied. You can only update your own profile or must be a Company Admin."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = EmployeeUpdateSerializer(
            employee,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        employee = EmployeeService.update_employee(
            employee,
            serializer.validated_data,
        )

        return Response(
            {
                "message": "Employee updated successfully.",
                "data": EmployeeDetailSerializer(employee).data,
            }
        )


class EmployeeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdmin]

    def delete(self, request, employee_id):
        employee = EmployeeService.get_employee(
            employee_id=employee_id,
            tenant=request.tenant,
        )

        EmployeeService.delete_employee(employee)
        # EmployeeService.soft_delete_employee(
        #     employee=employee,
        #     deleted_by=request.user,
        # )
        # evdee soft delete implement cheyyanm

        return Response(
            {
                "message": "Employee deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT,
        )


class BlockEmployeeAPIView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdmin]

    def post(self, request, employee_id):
        employee = EmployeeService.get_employee(
            employee_id=employee_id,
            tenant=request.tenant,
        )

        EmployeeService.block_employee(employee)

        return Response(
            {
                "message": "Employee blocked successfully."
            }
        )


class UnblockEmployeeAPIView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdmin]

    def post(self, request, employee_id):
        employee = EmployeeService.get_employee(
            employee_id=employee_id,
            tenant=request.tenant,
        )

        EmployeeService.unblock_employee(employee)

        return Response(
            {
                "message": "Employee unblocked successfully."
            }
        )