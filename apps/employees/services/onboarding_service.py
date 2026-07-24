from django.db import transaction

from apps.employees.services.employee_service import EmployeeService
from apps.employees.services.activation_service import ActivationService
from apps.employees.services.email_service import EmailService


class EmployeeOnboardingService:

    @staticmethod
    @transaction.atomic
    def create_employee(
        *,
        tenant,
        full_name,
        email,
        phone,
        role,
        department="",
        designation="",
        manager=None,
        address="",
        emergency_contact="",
        joined_at=None,
    ):
        """
        Complete employee onboarding flow.

        1. Create User
        2. Create UserTenant
        3. Create Employee
        4. Create Activation Token
        5. Send Activation Email
        """

        employee = EmployeeService.create_employee(
            tenant=tenant,
            full_name=full_name,
            email=email,
            phone=phone,
            role=role,
            department=department,
            designation=designation,
            manager=manager,
            address=address,
            emergency_contact=emergency_contact,
            joined_at=joined_at,
        )

        activation = ActivationService.create_activation(
            employee.user
        )

        EmailService.send_activation_email(
            tenant=tenant,
            user=employee.user,
            activation=activation,
        )

        return employee