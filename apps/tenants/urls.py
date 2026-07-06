from django.urls import path

from .views import (
    CompanyListAPIView,
    PendingCompanyAPIView,
    ApproveCompanyAPIView,
    RejectCompanyAPIView,
)

urlpatterns = [

    path(
        'companies/',
        CompanyListAPIView.as_view()
    ),

    path(
        'companies/pending/',
        PendingCompanyAPIView.as_view()
    ),

    path(
        'companies/<int:pk>/approve/',
        ApproveCompanyAPIView.as_view()
    ),

    path(
        'companies/<int:pk>/reject/',
        RejectCompanyAPIView.as_view()
    ),

]