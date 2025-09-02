from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.UserRegisterView.as_view(), name="user_register"),
    path("verify-email/", views.VerifyEmailView.as_view(), name="verify_email"),
    path("resend-verification/", views.ResendVerificationView.as_view(), name="resend_verification"),
]
