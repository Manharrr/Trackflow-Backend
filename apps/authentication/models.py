from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import check_password

from apps.tenants.models import Client


class OTPPurpose(models.TextChoices):
    REGISTER = "register", "Register"
    LOGIN = "login", "Login"
    PASSWORD_RESET = "password_reset", "Password Reset"


class PhoneOTP(models.Model):

    tenant = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    phone = models.CharField(
        max_length=15,
        db_index=True,
    )

    otp_hash = models.CharField(
        max_length=255,
    )

    purpose = models.CharField(
        max_length=30,
        choices=OTPPurpose.choices,
    )

    attempts = models.PositiveIntegerField(
        default=0,
    )

    is_verified = models.BooleanField(
        default=False,
    )

    expires_at = models.DateTimeField()

    used_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.phone} - {self.purpose}"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @classmethod
    def expiry_time(cls):
        return timezone.now() + timedelta(minutes=5)

  
# from django.db import models

# from datetime import timedelta
# from django.utils import timezone

# from apps.tenants.models import Client


# class OTPPurpose(models.TextChoices):
#     REGISTER = "register", "Register"
#     PASSWORD_RESET = "password_reset", "Password Reset"
#     LOGIN = "login", "Login"


# class PhoneOTP(models.Model):

#     tenant = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)

#     phone = models.CharField(max_length=15, db_index=True)

#     otp_hash = models.CharField(max_length=255)

#     purpose = models.CharField(max_length=30, choices=OTPPurpose.choices)

#     attempts = models.PositiveIntegerField(default=0)

#     is_verified = models.BooleanField(default=False)

#     expires_at = models.DateTimeField()

#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["-created_at"]

#     def is_expired(self):
#         return timezone.now() > self.expires_at

#     @classmethod
#     def expiry_time(cls):
#         return timezone.now() + timedelta(minutes=5)

#     def __str__(self):
#         return f"{self.phone} - {self.purpose}"