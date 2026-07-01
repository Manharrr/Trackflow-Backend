from django.urls import path

from .views import (
    CompanyRegisterAPIView,LoginAPIView,LogoutAPIView,RefreshAPIView,MeAPIView
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
]

# from django.urls import path
# from .views import RegisterView, LoginView, LogoutView, MeView

# urlpatterns = [
#     path('register/', RegisterView.as_view(), name='register'),
#     path('login/', LoginView.as_view(), name='login'),
#     path('logout/', LogoutView.as_view(), name='logout'),
#     path('me/', MeView.as_view(), name='me'),
# ]