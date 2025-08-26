from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.UserRegister.as_view(), name="user_register"),
    path("login/", views.UserLogin.as_view(), name="user_login"),
]
