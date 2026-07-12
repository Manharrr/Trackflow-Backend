from django.db import models

from django.conf import settings

from django_tenants.models import TenantMixin
from django_tenants.models import DomainMixin


class Client(TenantMixin):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    name = models.CharField(
        max_length=100
    )

    email = models.EmailField(
        unique=True
    )

    phone = models.CharField(
        max_length=15
    )

    verified = models.BooleanField(
        default=False
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    logo = models.ImageField(
        upload_to="company_logos/",
        blank=True,
        null=True,
    )

    address = models.TextField(
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    rejection_reason = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    auto_create_schema = False

    def __str__(self):
        return self.name


class Domain(DomainMixin):
    pass


class UserTenant(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workspaces",
    )

    tenant = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="user_tenants",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    is_active = models.BooleanField(
        default=True
    )
    

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "tenant",
                ],
                name="unique_user_per_tenant",
            )
        ]

    def __str__(self):

        return (
            f"{self.user.email} - {self.tenant.name}"
        )
    

    
# from django.db import models
# from django_tenants.models import TenantMixin
# from django_tenants.models import DomainMixin


# class Client(TenantMixin):
#     STATUS_CHOICES = (
#     ( 'pending','Pending'),
#     ('approved','Approved'),
#     ('rejected','Rejected' ),
# )
#     name = models.CharField(max_length=100)
#     phone = models.CharField(max_length=20)
#     email = models.EmailField(unique=True)
#     verified = models.BooleanField(default=False)

#     status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending'
#     )

#     logo = models.ImageField(
#     upload_to="company_logos/",
#     blank=True,
#     null=True,)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     address = models.TextField(blank=True)
#     description = models.TextField(blank=True)


#     rejection_reason = models.TextField(
#     blank=True,
#     null=True)

#     auto_create_schema = False


#     def __str__(self):
#         return self.name


# class Domain(DomainMixin):
#     pass