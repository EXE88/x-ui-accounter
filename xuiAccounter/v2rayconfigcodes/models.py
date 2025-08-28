from django.db import models
import uuid
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class ConfigCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.CharField(max_length=100)
    total_gb = models.BigIntegerField(default=0)
    expiry_time = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    