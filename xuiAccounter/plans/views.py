from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Plan

class GetPlans(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        all_plans = Plan.objects.all()
        plans_data = []
        for plan in all_plans:
            plans_data.append({
                "id": plan.id,
                "plan_name": plan.plan_name,
                "number_of_users": plan.number_of_users,
                "time": plan.time,
                "usage": plan.usage,
                "price": plan.price,
            })
        return Response({"plans": plans_data}, status=200)
            
