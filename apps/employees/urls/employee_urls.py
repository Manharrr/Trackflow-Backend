from django.urls import path

from apps.employees.views.employee_views import (
    EmployeeCreateAPIView,
    EmployeeListAPIView,
    EmployeeDetailAPIView,
    EmployeeUpdateAPIView,
    EmployeeDeleteAPIView,
    BlockEmployeeAPIView,
    UnblockEmployeeAPIView,
)

urlpatterns = [
    path("", EmployeeListAPIView.as_view(), name="employee-list"),
    path("create/", EmployeeCreateAPIView.as_view(), name="employee-create"),
    path("<uuid:employee_id>/", EmployeeDetailAPIView.as_view(), name="employee-detail"),
    path("<uuid:employee_id>/update/", EmployeeUpdateAPIView.as_view(), name="employee-update"),
    path("<uuid:employee_id>/delete/", EmployeeDeleteAPIView.as_view(), name="employee-delete"),
    path("<uuid:employee_id>/block/", BlockEmployeeAPIView.as_view(), name="employee-block"),
    path("<uuid:employee_id>/unblock/", UnblockEmployeeAPIView.as_view(), name="employee-unblock"),
]