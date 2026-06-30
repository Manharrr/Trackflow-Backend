from django.db import models
from django_tenants.models import TenantMixin
from django_tenants.models import DomainMixin


class Client(TenantMixin):
    name = models.CharField(max_length=100)

    phone = models.CharField(max_length=20)

    email = models.EmailField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    auto_create_schema = True


class Domain(DomainMixin):
    pass