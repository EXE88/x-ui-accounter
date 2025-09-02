from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.conf import settings

class UserMetaData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    last_sent_at = models.DateTimeField(null=True, blank=True)

    def is_expired(self):
        minutes = getattr(settings, "EMAIL_VERIFICATION_EXPIRE_MINUTES", 10)
        return timezone.now() > self.created_at + timedelta(minutes=minutes)

    def time_remaining_seconds(self):
        minutes = getattr(settings, "EMAIL_VERIFICATION_EXPIRE_MINUTES", 10)
        expiry = self.created_at + timedelta(minutes=minutes)
        remaining = (expiry - timezone.now()).total_seconds()
        return max(0, int(remaining))

    def seconds_since_last_send(self):
        if not self.last_sent_at:
            return None
        return int((timezone.now() - self.last_sent_at).total_seconds())

    def can_send_again(self, cooldown_seconds):
        if not self.last_sent_at:
            return True, 0
        elapsed = (timezone.now() - self.last_sent_at).total_seconds()
        if elapsed >= cooldown_seconds:
            return True, 0
        return False, int(cooldown_seconds - elapsed)
