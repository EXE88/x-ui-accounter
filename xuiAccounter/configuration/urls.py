from django.urls import path
from . import views

urlpatterns = [
    path("",views.ConfigurePageView.as_view(),name="admin_config")
]
