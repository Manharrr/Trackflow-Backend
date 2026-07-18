from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User
from apps.tenants.models import UserTenant
from apps.employees.models import Employee, Invitation


def send_invitation_email(invitation):
    """
    Sends an invitation email containing the acceptance signup link
    pointing to the tenant's workspace subdomain.
    """
    tenant = invitation.tenant
    # Accept URL maps to the company subdomain: e.g. http://company.localhost:5173/accept-invitation?token=<uuid>
    # accept_url = f"http://{tenant.schema_name}.localhost:5173/accept-invitation?token={invitation.invitation_token}"
    accept_url = (
        f"http://{tenant.schema_name}.trackflow.local:5173/"
        f"accept-invitation?token={invitation.invitation_token}"
    )

    subject = f"Invitation to join {tenant.name} on TrackFlow AI"
    message = f"""Hello {invitation.full_name},

You have been invited by {invitation.invited_by.full_name if invitation.invited_by else 'Admin'} to join {tenant.name} as a {invitation.get_role_display()}.

To accept this invitation and set up your account, please click the link below:

{accept_url}

This invitation link will expire in 7 days.

Best regards,
TrackFlow AI Team
"""
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[invitation.email],
        fail_silently=True,
    )


def create_employee_invitation(tenant, invited_by, full_name, email, phone, role):
    """
    Generates an invitation, saves it, and dispatches the invitation email.
    """
    # Double check if an active employee profile or pending invitation exists
    if Employee.objects.filter(tenant=tenant, email=email).exists():
        raise ValidationError(
            {"email": "An employee with this email already exists in this workspace."}
        )

    Invitation.objects.filter(
        tenant=tenant,
        email=email,
        is_accepted=False,
    ).delete()

    expires_at = timezone.now() + timedelta(days=7)

    invitation = Invitation.objects.create(
        tenant=tenant,
        invited_by=invited_by,
        full_name=full_name,
        email=email,
        phone=phone,
        role=role,
        expires_at=expires_at,
    )

    send_invitation_email(invitation)
    return invitation


@transaction.atomic
def accept_employee_invitation(token, password):
    """
    Resolves the invitation token, registers the User (if required),
    establishes schema authorization mappings, and instantiates the Employee profile.
    """
    try:
        invitation = Invitation.objects.select_related("tenant").get(
            invitation_token=token,
            is_accepted=False,
        )
    except Invitation.DoesNotExist:
        raise ValidationError({"token": "Invalid or already accepted invitation token."})

    if timezone.now() > invitation.expires_at:
        raise ValidationError({"token": "Invitation token has expired."})

    email = invitation.email
    phone = invitation.phone
    tenant = invitation.tenant

    # Find or Create Django User
    user = User.objects.filter(email=email).first()
    if not user:
        # Check if phone number is already occupied
        if User.objects.filter(phone=phone).exists():
            raise ValidationError(
                {"phone": "Phone number is already associated with another account."}
            )

        # Create new User
        user = User.objects.create_user(
            username=email,
            email=email,
            phone=phone,
            password=password,
        )
        user.is_verified = True
        user.save()
    else:
        # If user exists, verify they have access to password update if they need it
        # or link their password if it was blank
        if not user.has_usable_password():
            user.set_password(password)
            user.save()

    # Create UserTenant relation to allow workspace login
    UserTenant.objects.get_or_create(
        user=user,
        tenant=tenant,
        defaults={"is_active": True},
    )

    # Create Employee profile
    employee = Employee.objects.create(
        tenant=tenant,
        user=user,
        role=invitation.role,
        full_name=invitation.full_name,
        email=email,
        phone=phone,
        is_active=True,
        is_blocked=False,
        first_login=True,
    )

    # Mark invitation as accepted
    invitation.is_accepted = True
    invitation.save(update_fields=["is_accepted"])

    return employee
