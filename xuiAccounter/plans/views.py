from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Plan
from coins.models import Coin
from v2rayconfigcodes.models import GlobalVariables, ConfigCode
import requests
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import uuid
import string
import random

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
    
class BuyPlan(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            plan_id = request.POST.get("plan_id")
            if plan_id is None or not str(plan_id).isdigit():
                return Response({"error": "Invalid or missing plan_id."}, status=400)

            try:
                plan_obj = Plan.objects.get(id=plan_id)
            except Plan.DoesNotExist:
                return Response({"error": "Plan not found."}, status=404)

            try:
                user_coins = Coin.objects.get(user=request.user)
            except Coin.DoesNotExist:
                return Response({"error": "User coins not found."}, status=404)

            price = plan_obj.price
            if user_coins.number_of_coins < price:
                return Response({"error": "Not enough coins to purchase this plan."}, status=400)

            global_variables = GlobalVariables.objects.all().first()
            if not global_variables:
                return Response({"error": "Global variables not configured."}, status=500)

            base_url = f"http://{global_variables.panel_address}:{global_variables.panel_port}"

            try:
                login_response = requests.post(
                    f"{base_url}/login",
                    data={
                        "username": global_variables.panel_username,
                        "password": global_variables.panel_password
                    },
                    timeout=10
                )
                login_response.raise_for_status()
            except requests.RequestException as e:
                return Response({"error": "Failed to connect to panel.", "details": str(e)}, status=502)

            cookie_jar = login_response.cookies
            cookie = requests.utils.dict_from_cookiejar(cookie_jar)

            usage_as_bytes = plan_obj.usage * 1024**3
            future_date = datetime.now() + relativedelta(months=plan_obj.time)
            time_as_timestamp_ms = int(future_date.timestamp() * 1000)
            client_id = str(uuid.uuid4())
            email = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            subid = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

            payload = {
                "id": global_variables.inbound_id,
                "settings": json.dumps({
                    "clients": [
                        {
                            "id": client_id,
                            "flow": "",
                            "email": email,
                            "limitIp": 0,
                            "totalGB": usage_as_bytes,
                            "expiryTime": time_as_timestamp_ms,
                            "enable": True,
                            "tgId": "",
                            "subId": subid,
                            "comment": "",
                            "reset": 0
                        }
                    ]
                })
            }

            try:
                response = requests.post(
                    f"{base_url}/panel/inbound/addClient",
                    data=payload,
                    cookies=cookie,
                    verify=False,
                    timeout=10
                )
                response.raise_for_status()
                response_json = response.json()
            except requests.RequestException as e:
                return Response({"error": "Failed to add client to panel.", "details": str(e)}, status=502)
            except ValueError:
                return Response({"error": "Invalid response from panel."}, status=502)

            if response_json['success']  == True and response.status_code == 200:
                user_coins.number_of_coins -= price
                user_coins.save()

                new_config_code = ConfigCode.objects.create(
                    user=request.user,
                    client_id=client_id,
                    email=email,
                    total_gb=usage_as_bytes,
                    expiry_time=time_as_timestamp_ms
                )
                new_config_code.save()

                data = {
                    "status": "success",
                    "details": {
                        "plan_name": plan_obj.plan_name,
                        "number_of_users": plan_obj.number_of_users,
                        "time": plan_obj.time,
                        "usage": plan_obj.usage,
                        "price": plan_obj.price,
                        "config_code":f"vless://{client_id}@{global_variables.panel_address}:{global_variables.x_ui_listen_port}?type=tcp#Iran-{email}"
                    }
                }
                return Response(data, 200)
            else:
                return Response({"error": "Panel did not accept client.", "details": response_json}, status=502)

        except Exception as e:
            return Response({"error": "Unexpected error occurred.", "details": str(e)}, status=500)