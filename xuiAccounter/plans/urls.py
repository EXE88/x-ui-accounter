from django.urls import path
from . import views

urlpatterns = [
    path("", views.GetPlans.as_view(), name="get_plans"),
    path("buy/", views.BuyPlan.as_view(), name="buy_plan")
]
