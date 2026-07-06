from rest_framework import serializers

from .models import Client


class CompanySerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = Client

        fields = [
            'id',
            'name',
            'schema_name',
            'phone',
            'email',
            'status',
            'created_at',
        ]