from dotenv import dotenv_values
from django.conf import settings
from .models import GlobalVariables
import os

#dont forget to add cronjob useing this command on linux : python3 manage.py crontab add 

def update_model():
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

