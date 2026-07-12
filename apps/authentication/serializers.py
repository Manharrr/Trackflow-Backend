from rest_framework import serializers

from apps.accounts.models import User
from apps.tenants.models import Client


class CompanyRegisterSerializer(
    serializers.Serializer
):

    company_name = serializers.CharField(
        max_length=100
    )

    admin_name = serializers.CharField(
        max_length=100
    )

    email = serializers.EmailField()

    phone = serializers.CharField(
        max_length=15
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    confirm_password = serializers.CharField(
        write_only=True,
    )
    workspace_code = serializers.CharField(
        max_length=50,
    )
    if Client.objects.filter(
        schema_name=attrs["workspace_code"] 
    ).exists():
        raise serializers.ValidationError(
            {
                "workspace_code":
                "Workspace already exists."
            }
        )
    

    def validate(
        self,
        attrs,
    ):

        if (
            attrs["password"]
            !=
            attrs["confirm_password"]
        ):
            raise serializers.ValidationError(
                {
                    "confirm_password":
                    "Passwords do not match."
                }
            )

        if User.objects.filter(
            email=attrs["email"]
        ).exists():

            raise serializers.ValidationError(
                {
                    "email":
                    "Email already registered."
                }
            )

        if User.objects.filter(
            phone=attrs["phone"]
        ).exists():

            raise serializers.ValidationError(
                {
                    "phone":
                    "Phone already registered."
                }
            )

        return attrs


class VerifyOTPSerializer(
    serializers.Serializer
):

    phone = serializers.CharField(
        max_length=15
    )

    otp = serializers.CharField(
        max_length=6
    )


class LoginSerializer(
    serializers.Serializer
):

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True
    )


class GoogleLoginSerializer(
    serializers.Serializer
):

    token = serializers.CharField()


class ForgotPasswordSerializer(
    serializers.Serializer
):

    phone = serializers.CharField(
        max_length=15
    )


class VerifyForgotOTPSerializer(
    serializers.Serializer
):

    phone = serializers.CharField(
        max_length=15
    )

    otp = serializers.CharField(
        max_length=6
    )


class ResetPasswordSerializer(
    serializers.Serializer
):

    phone = serializers.CharField(
        max_length=15
    )

    password = serializers.CharField(
        min_length=8,
        write_only=True,
    )

    confirm_password = serializers.CharField(
        write_only=True,
    )

    def validate(
        self,
        attrs,
    ):

        if (
            attrs["password"]
            !=
            attrs["confirm_password"]
        ):
            raise serializers.ValidationError(
                {
                    "confirm_password":
                    "Passwords do not match."
                }
            )

        return attrs


class MFASetupSerializer(
    serializers.Serializer
):
    pass


class MFAVerifySerializer(
    serializers.Serializer
):

    code = serializers.CharField(
        max_length=6
    )


class MFALoginSerializer(
    serializers.Serializer
):

    email = serializers.EmailField()

    code = serializers.CharField(
        max_length=6
    )
# from rest_framework import serializers
# from django.contrib.auth import get_user_model

# User = get_user_model()

# # class RegisterSerializer(serializers.ModelSerializer):
# #     password = serializers.CharField(write_only=True, min_length=8)
# #     confirm_password = serializers.CharField(write_only=True)

# #     class Meta:
# #         model = User
# #         fields = ['email', 'username', 'password', 'confirm_password']

# #     def validate(self, data):
# #         if data['password'] != data['confirm_password']:
# #             raise serializers.ValidationError("Passwords do not match")
# #         return data

# #     def create(self, validated_data):
# #         validated_data.pop('confirm_password')
# #         user = User.objects.create_user(
# #             email=validated_data['email'],
# #             username=validated_data['username'],
# #             password=validated_data['password'],
# #         )
# #         return user


# class LoginSerializer(serializers.Serializer):
#     phone = serializers.CharField(max_length=15)
#     password = serializers.CharField(write_only=True)


# class CompanyRegisterSerializer(serializers.Serializer):
#     company_name = serializers.CharField(max_length=100)
#     subdomain = serializers.CharField(max_length=50)
#     admin_name = serializers.CharField(max_length=100)
#     email = serializers.EmailField()
#     phone = serializers.CharField(max_length=15)
#     password = serializers.CharField(write_only=True)
#     confirm_password = serializers.CharField(write_only=True)

#     def validate(
#         self,
#         attrs
#     ):
#         if (
#             attrs["password"]
#             !=
#             attrs["confirm_password"]
#         ):
#             raise serializers.ValidationError(
#                 "Passwords do not match"
#             )

#         if User.objects.filter(
#             email=attrs["email"]
#         ).exists():
#             raise serializers.ValidationError(
#                 {
#                     "email":
#                     "Email already exists"
#                 }
#             )

#         if User.objects.filter(
#             phone=attrs["phone"]
#         ).exists():
#             raise serializers.ValidationError(
#                 {
#                     "phone":
#                     "Phone number already exists"
#                 }
#             )

#         return attrs

# class VerifyPhoneSerializer(
#     serializers.Serializer
# ):
#     phone = serializers.CharField()
#     otp = serializers.CharField(
#         max_length=6
#     )