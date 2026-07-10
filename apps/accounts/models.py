from django.db import models

from django.contrib.auth.models import AbstractUser


class Role(models.TextChoices):
    SUPER_ADMIN = 'super_admin', 'Super Admin'
    COMPANY_ADMIN = 'company_admin', 'Company Admin'
    OPERATIONS_MANAGER = 'operations_manager', 'Operations Manager'
    EMPLOYEE = 'employee', 'Employee'

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True,)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE
    )
    is_mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=64, blank=True, null=True)
    phone_verified = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    # @property

    @property
    def is_admin(self):
        return self.role in [
            Role.SUPER_ADMIN,
            Role.COMPANY_ADMIN,
        ]

 