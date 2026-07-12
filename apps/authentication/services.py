import random
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.hashers import (
    make_password,
)

from django.core.mail import (
    send_mail,
)

from rest_framework_simplejwt.tokens import (
    RefreshToken,
)

from twilio.rest import Client as TwilioClient

import pyotp

from .models import (
    PhoneOTP,
)

from apps.accounts.models import (
    User,
)


# ==========================================
# OTP
# ==========================================

def generate_otp():

    return str(
        random.randint(
            100000,
            999999,
        )
    )


def create_phone_otp(
    phone,
    purpose,
):

    PhoneOTP.objects.filter(
        phone=phone,
        purpose=purpose,
        is_verified=False,
    ).delete()

    otp = generate_otp()

    PhoneOTP.objects.create(
        phone=phone,
        purpose=purpose,
        otp_hash=make_password(
            otp
        ),
        expires_at=PhoneOTP.expiry_time(),
    )

    return otp


def verify_phone_otp(
    phone,
    otp,
    purpose,
):

    try:

        record = (
            PhoneOTP.objects.filter(
                phone=phone,
                purpose=purpose,
                is_verified=False,
            ).latest("created_at")
        )

    except PhoneOTP.DoesNotExist:

        return None

    if record.is_expired:

        return None

    if not record.verify(otp):

        record.attempts += 1

        record.save(
            update_fields=[
                "attempts",
            ]
        )

        return None

    record.is_verified = True

    record.used_at = timezone.now()

    record.save(
        update_fields=[
            "is_verified",
            "used_at",
        ]
    )

    return record


# ==========================================
# SMS
# ==========================================

def send_sms(
    phone,
    message,
):

    client = TwilioClient(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN,
    )

    client.messages.create(
        body=message,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone,
    )


def send_otp_sms(
    phone,
    otp,
):

    message = (
        f"Your TrackFlow AI OTP is {otp}"
    )

    send_sms(
        phone,
        message,
    )


# ==========================================
# EMAIL
# ==========================================

def send_password_reset_email(
    email,
):

    send_mail(
        subject="Password Reset",
        message=(
            "Password reset request received."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[
            email
        ],
    )


# ==========================================
# JWT
# ==========================================

def generate_tokens(
    user,
):

    refresh = (
        RefreshToken.for_user(
            user
        )
    )

    return {

        "refresh": str(
            refresh
        ),

        "access": str(
            refresh.access_token
        ),
    }


# ==========================================
# MFA
# ==========================================

def generate_mfa_secret(
    user,
):

    if not user.mfa_secret:

        user.mfa_secret = (
            pyotp.random_base32()
        )

        user.save(
            update_fields=[
                "mfa_secret",
            ]
        )

    return user.mfa_secret


def verify_mfa(
    user,
    code,
):

    if not user.mfa_secret:

        return False

    totp = pyotp.TOTP(
        user.mfa_secret
    )

    return totp.verify(
        code
    )


# ==========================================
# USER
# ==========================================

def create_user(
    *,
    email,
    phone,
    password,
):

    return User.objects.create_user(

        username=email,

        email=email,

        phone=phone,

        password=password,
    )
# from twilio.rest import Client
# from django.conf import settings


# def send_sms(phone, message):

#     print("=" * 50)
#     print("FROM :", settings.TWILIO_PHONE_NUMBER)
#     print("TO   :", phone)
#     print("=" * 50)

#     client = Client(
#         settings.TWILIO_ACCOUNT_SID,
#         settings.TWILIO_AUTH_TOKEN
#     )

#     message = client.messages.create(
#         body=message,
#         from_=settings.TWILIO_PHONE_NUMBER,
#         to=phone
#     )

#     print("SID :", message.sid)