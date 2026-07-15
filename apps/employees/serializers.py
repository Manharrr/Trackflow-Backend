from rest_framework import serializers

from apps.employees.models import Employee, Invitation, Role


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ["id", "full_name", "email", "phone", "role"]

    def validate(self, attrs):
        request = self.context.get("request")
        if request and hasattr(request, "tenant"):
            tenant = request.tenant
            # Check if this email is already a registered employee in the current tenant
            if Employee.objects.filter(tenant=tenant, email=attrs["email"]).exists():
                raise serializers.ValidationError(
                    {"email": "An employee with this email already exists in this workspace."}
                )
            # Check if there is already an active unexpired invitation
            from django.utils import timezone
            if Invitation.objects.filter(
                tenant=tenant,
                email=attrs["email"],
                is_accepted=False,
                expires_at__gt=timezone.now()
            ).exists():
                raise serializers.ValidationError(
                    {"email": "A pending invitation already exists for this email."}
                )
        return attrs


class AcceptInvitationSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return attrs


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "id",
            "user",
            "role",
            "full_name",
            "email",
            "phone",
            "profile_image",
            "department",
            "designation",
            "manager",
            "address",
            "emergency_contact",
            "is_active",
            "is_blocked",
            "first_login",
            "password_changed",
            "joined_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "email", "created_at", "updated_at"]


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "full_name",
            "phone",
            "profile_image",
            "department",
            "designation",
            "address",
            "emergency_contact",
            "joined_at",
        ]
