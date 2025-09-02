from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from .models import UserMetaData, EmailVerification
from coins.models import Coin
import logging

#dont forget to add cronjob useing this command on linux : python3 manage.py crontab add 

logger = logging.getLogger(__name__)

from django.conf import settings
EXPIRE_MINUTES = getattr(settings, "UNVERIFIED_EXPIRE_MINUTES", 10)

def cleanup_unverified():
    cutoff = timezone.now() - timedelta(minutes=EXPIRE_MINUTES)
    qs = User.objects.filter(is_active=False, date_joined__lt=cutoff)
    deleted_count = 0
    for u in qs:
        try:
            EmailVerification.objects.filter(user=u).delete()
            UserMetaData.objects.filter(user=u).delete()
            Coin.objects.filter(user=u).delete()
            u.delete()
            deleted_count += 1
        except Exception as e:
            logger.exception(f"Failed to delete unverified user id={u.id}, username={u.username}: {e}")
    logger.info(f"cleanup_unverified: deleted {deleted_count} users older than {EXPIRE_MINUTES} minutes")
