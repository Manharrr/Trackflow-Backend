from django.urls import path
from .views import (
    InviteEmployeeAPIView,
    AcceptInvitationAPIView,
    EmployeeListAPIView,
    EmployeeDetailAPIView,
    BlockEmployeeAPIView,
    UnblockEmployeeAPIView,
)

urlpatterns = [
    # Employee invitations
    path("invitations/", InviteEmployeeAPIView.as_view(), name="employee-invite"),
    path("invitations/accept/", AcceptInvitationAPIView.as_view(), name="employee-accept-invite"),

    # Employee profile CRUD
    path("profiles/", EmployeeListAPIView.as_view(), name="employee-list"),
    path("profiles/<uuid:pk>/", EmployeeDetailAPIView.as_view(), name="employee-detail"),

    # Employee status control
    path("profiles/<uuid:pk>/block/", BlockEmployeeAPIView.as_view(), name="employee-block"),
    path("profiles/<uuid:pk>/unblock/", UnblockEmployeeAPIView.as_view(), name="employee-unblock"),
]
