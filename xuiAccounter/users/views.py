# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import UserMetaDataSerializer
from coins.models import Coin
from .models import EmailVerification, UserMetaData
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import random
import re
from django.core.mail import send_mail

UNVERIFIED_EXPIRE_MINUTES = getattr(settings, "UNVERIFIED_EXPIRE_MINUTES", 10)
EMAIL_VERIFICATION_EXPIRE_MINUTES = getattr(settings, "EMAIL_VERIFICATION_EXPIRE_MINUTES", 10)
COOLDOWN_SECONDS = getattr(settings, "EMAIL_RESEND_COOLDOWN_SECONDS", 60)

class SendCode:
    def send_verification_email(email, code):
        subject = "Verification code"
        message = f"Your verification code is: {code}"
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@yourdomain.com")
        send_mail(subject, message, from_email, [email], fail_silently=False)

class UserRegisterView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")

        if not username or not password or not email:
            return Response({"error": "please send all required fields"}, status=400)
        if len(password) < 8 or len(password) > 128:
            return Response({"error": "Password length invalid. at least pasword must have 8 characters"}, status=400)
        if len(username) < 8 or len(username) > 128:
            return Response({"error": "username length invalid. at least username must have 8 characters"}, status=400)
        if not re.match(r'^[\w.@+-]+$', username):
            return Response({"error": "username contains invalid characters."}, status=403)
        
        existing_user = User.objects.filter(username=username).first()
        if existing_user:
            if not existing_user.is_active:
                cutoff = existing_user.date_joined + timedelta(minutes=UNVERIFIED_EXPIRE_MINUTES)
                remaining = (cutoff - timezone.now()).total_seconds()
                if remaining > 0:
                    minutes = int(remaining // 60) + 1
                    return Response({"error": f"Username reserved for verification. Try again in ~{minutes} minute(s) or choose another username."}, status=409)
            return Response({"error": "A user with this username already exists."}, status=409)

        existing_meta = UserMetaData.objects.filter(email=email).first()
        if existing_meta:
            meta_user = existing_meta.user
            if not meta_user.is_active:
                cutoff = meta_user.date_joined + timedelta(minutes=UNVERIFIED_EXPIRE_MINUTES)
                remaining = (cutoff - timezone.now()).total_seconds()
                if remaining > 0:
                    minutes = int(remaining // 60) + 1
                    return Response({"error": f"Email reserved for verification. Try again in ~{minutes} minute(s) or use a different email."}, status=409)
            return Response({"error": "This email is already in use."}, status=409)

        try:
            with transaction.atomic():
                new_user = User(username=username, is_active=False)
                new_user.set_password(password)
                new_user.save()

                meta_serializer = UserMetaDataSerializer(data={"email": email})
                if not meta_serializer.is_valid():
                    raise ValueError(meta_serializer.errors)
                meta_serializer.save(user=new_user)

                code = f"{random.randint(100000, 999999):06d}"
                EmailVerification.objects.update_or_create(
                    user=new_user,
                    defaults={"code": code, "created_at": timezone.now(), "last_sent_at":timezone.now()}
                )
                SendCode.send_verification_email(email, code)

                return Response({"info": "account created. verification email sent."}, status=201)
        except ValueError as ve:
            return Response({"error": str(ve)}, status=400)
        except Exception as e:
            return Response({"error": f"Error creating account: {str(e)}"}, status=500)


class VerifyEmailView(APIView):
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")
        if not email or not code:
            return Response({"error": "email and code required"}, status=400)

        try:
            meta = UserMetaData.objects.get(email=email)
            user = meta.user
        except UserMetaData.DoesNotExist:
            return Response({"error": "Invalid email or code."}, status=400)

        try:
            ev = EmailVerification.objects.get(user=user)
        except EmailVerification.DoesNotExist:
            return Response({"error": "Verification code not found. Request new code."}, status=400)

        if ev.code != code:
            return Response({"error": "Invalid verification code."}, status=400)
        if ev.is_expired():
            return Response({"error": "Code expired. Request new code."}, status=400)

        try:
            with transaction.atomic():
                user.is_active = True
                user.save()
                ev.delete()
                Coin.objects.get_or_create(user=user, defaults={"number_of_coins": 0})
                return Response({"info": "Email verified. You can now login."}, status=200)
        except Exception as e:
            return Response({"error": f"Error verifying account: {str(e)}"}, status=500)


class ResendVerificationView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "email required"}, status=400)

        try:
            meta = UserMetaData.objects.get(email=email)
            user = meta.user
        except UserMetaData.DoesNotExist:
            return Response({"error": "No account found with this email."}, status=400)

        if user.is_active:
            return Response({"error": "Account already active."}, status=400)

        ev = None
        try:
            ev = EmailVerification.objects.get(user=user)
        except EmailVerification.DoesNotExist:
            ev = None

        now = timezone.now()

        if ev is None:
            code = f"{random.randint(100000, 999999):06d}"
            ev = EmailVerification.objects.create(user=user, code=code, last_sent_at=now)
            SendCode.send_verification_email(email, code)
            return Response({"info": "Verification code sent."}, status=200)

        can_send, secs_left = ev.can_send_again(COOLDOWN_SECONDS)
        if not can_send:
            return Response({
                "error": "Please wait before requesting another verification email.",
                "seconds_until_next_send": secs_left
            }, status=429)

        if not ev.is_expired():
            secs = ev.time_remaining_seconds()
            minutes = secs // 60
            seconds = secs % 60
            return Response({
                "error": "Current verification code is still valid.",
                "time_remaining_seconds": secs,
                "message": f"Please use the existing code or wait ~{minutes} minute(s) and {seconds} second(s)."
            }, status=429)

        code = f"{random.randint(100000, 999999):06d}"
        ev.code = code
        ev.created_at = now
        ev.last_sent_at = now
        ev.save()
        SendCode.send_verification_email(email, code)
        return Response({"info": "New verification code sent."}, status=200)
