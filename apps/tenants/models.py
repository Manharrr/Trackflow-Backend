from django.db import models
from django_tenants.models import TenantMixin
from django_tenants.models import DomainMixin


class Client(TenantMixin):
    STATUS_CHOICES = (
    ( 'pending','Pending'),
    ('approved','Approved'),
    ('rejected','Rejected' ),
)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending'
    )
    verified = models.BooleanField(default=False)

    logo = models.ImageField(
    upload_to="company_logos/",
    blank=True,
    null=True,)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    address = models.TextField(blank=True)
    description = models.TextField(blank=True)


    rejection_reason = models.TextField(
    blank=True,
    null=True)

    auto_create_schema = False


    def __str__(self):
        return self.name


class Domain(DomainMixin):
    pass