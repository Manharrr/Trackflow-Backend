from rest_framework import serializers

from apps.employees.models import Employee, Role


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """
    Used by Company Admin while creating employees.
    """

    class Meta:
        model = Employee

        fields = (
            "full_name",
            "email",
            "phone",
            "role",
            "department",
            "designation",
            "manager",
            "address",
            "emergency_contact",
            "joined_at",
        )

    def validate_role(self, value):

        if value not in [
            Role.OPERATIONS_MANAGER,
            Role.EMPLOYEE,
        ]:
            raise serializers.ValidationError(
                "Only Operations Manager and Employee roles are allowed."
            )

        return value

    def validate(self, attrs):

        tenant = self.context["request"].tenant

        if Employee.objects.filter(
            tenant=tenant,
            email=attrs["email"],
        ).exists():
            raise serializers.ValidationError(
                {
                    "email":
                    "Employee with this email already exists."
                }
            )

        if Employee.objects.filter(
            tenant=tenant,
            phone=attrs["phone"],
        ).exists():
            raise serializers.ValidationError(
                {
                    "phone":
                    "Employee with this phone already exists."
                }
            )

        return attrs


class EmployeeListSerializer(serializers.ModelSerializer):

    manager_name = serializers.CharField(
        source="manager.full_name",
        read_only=True,
    )

    class Meta:

        model = Employee

        fields = (
            "id",
            "full_name",
            "email",
            "phone",
            "role",
            "department",
            "designation",
            "manager_name",
            "is_active",
            "is_blocked",
        )


class EmployeeDetailSerializer(serializers.ModelSerializer):

    manager_name = serializers.CharField(
        source="manager.full_name",
        read_only=True,
    )

    class Meta:

        model = Employee

        fields = "__all__"


class EmployeeUpdateSerializer(serializers.ModelSerializer):

    class Meta:

        model = Employee

        fields = (
            "full_name",
            "phone",
            "department",
            "designation",
            "manager",
            "address",
            "emergency_contact",
            "profile_image",
            "joined_at",
        )

    def validate_phone(self, value):

        employee = self.instance

        exists = Employee.objects.filter(
            tenant=employee.tenant,
            phone=value,
        ).exclude(
            id=employee.id,
        ).exists()

        if exists:
            raise serializers.ValidationError(
                "Phone already exists."
            )

        return value