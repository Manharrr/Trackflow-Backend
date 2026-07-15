from django.contrib import admin
from .models import Employee, Invitation


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tenant",
        "user",
        "role",
        "full_name",
        "email",
        "phone",
        "is_active",
        "is_blocked",
    )
    list_filter = ("role", "is_active", "is_blocked")
    search_fields = ("full_name", "email", "phone")
    ordering = ("-created_at",)


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tenant",
        "invited_by",
        "full_name",
        "email",
        "phone",
        "role",
        "is_accepted",
        "expires_at",
        "created_at",
    )
    list_filter = ("role", "is_accepted")
    search_fields = ("full_name", "email", "phone", "invitation_token")
    ordering = ("-created_at",)
