from dotenv import dotenv_values
from django.conf import settings
from .models import GlobalVariables, ConfigCode
import os
import requests

#dont forget to add cronjob useing this command on linux : python3 manage.py crontab add 

def update_globalvariables():
    env_path = os.path.join(settings.BASE_DIR, ".env")
    config = dotenv_values(env_path)
    
    model = GlobalVariables.objects.first()
    model.panel_address = config.get("X_UI_PANEL_DOMAIN")
    model.panel_port = config.get("X_UI_PANEL_DOMAIN_PORT")
    model.panel_username = config.get("X_UI_PANEL_USERNAME")
    model.panel_password = config.get("X_UI_PANEL_PASSWORD")
    model.x_ui_listen_port = config.get("LISTEN_PORT")
    model.inbound_id = config.get("INBOUND_ID")
    model.save()

def update_configs_status():
    global_variables = GlobalVariables.objects.all().first()
    if not global_variables:
        print("GlobalVariables object not found.")
        return

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
        print(f"Failed to connect to panel. Details: {str(e)}")
        return

    cookie_jar = login_response.cookies
    cookie = requests.utils.dict_from_cookiejar(cookie_jar)

    try:
        response = requests.post(f"{base_url}/panel/inbound/list", cookies=cookie, verify=False, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Failed to fetch inbound list. Details: {str(e)}")
        return
    except ValueError:
        print("Failed to parse JSON response.")
        return

    try:
        inbound_id = int(global_variables.inbound_id)
    except (TypeError, ValueError):
        print("Invalid inbound_id in GlobalVariables.")
        return

    inbound_obj = next(
        (inbound for inbound in data.get("obj", []) if inbound.get("id") == inbound_id),
        None
    )

    if not inbound_obj:
        print("Inbound object not found.")
        return

    client_stats = inbound_obj.get("clientStats", [])
    email_map = {client.get("email"): client for client in client_stats if client.get("email")}
    configs = ConfigCode.objects.filter(email__in=email_map.keys())
    for cfg in configs:
        stats = email_map.get(cfg.email)
        if not stats:
            continue

        try:
            configCode_obj = ConfigCode.objects.filter(email=stats['email']).first()
            if configCode_obj:
                configCode_obj.expiry_time = stats.get('expiryTime')
                total = stats.get('total', 0)
                up = stats.get('up', 0)
                down = stats.get('down', 0)
                configCode_obj.total_gb = total - (up + down)
                configCode_obj.save()
        except Exception as e:
            print(f"Error updating config for {cfg.email}: {str(e)}")