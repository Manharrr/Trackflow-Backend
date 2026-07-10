from django.contrib import admin

# Register your models here.

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "username",
        "email",
        "phone",
        "role",
        "phone_verified",
        "is_mfa_enabled",
    )

    search_fields = (
        "email",
        "phone",
        "username",
    )

    list_filter = (
        "role",
        "phone_verified",
        "is_mfa_enabled",
    )