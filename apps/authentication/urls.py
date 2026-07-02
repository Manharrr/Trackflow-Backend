from django.urls import path

from .views import (
    CompanyRegisterAPIView,LoginAPIView,LogoutAPIView,RefreshAPIView,MeAPIView,VerifyPhoneAPIView,CompanyListAPIView,ApproveCompanyAPIView,RejectCompanyAPIView
)

urlpatterns = [
    path(
        "register-company/", CompanyRegisterAPIView.as_view()),
        
         path(
        "login/",
        LoginAPIView.as_view()
    ),
    path(
        "logout/",
        LogoutAPIView.as_view()
    ),
    path(
        "token/refresh/",
        RefreshAPIView.as_view()
    ),
    path(
        "me/",
        MeAPIView.as_view()
    ),

    path(
        'verify-phone/',
        VerifyPhoneAPIView.as_view()
    ),

    path(
        'admin/companies/',
        CompanyListAPIView.as_view()
    ),

    path(
        'admin/companies/<int:pk>/approve/',
        ApproveCompanyAPIView.as_view()
    ),

    path(
        'admin/companies/<int:pk>/reject/',
        RejectCompanyAPIView.as_view()
    ),
]

