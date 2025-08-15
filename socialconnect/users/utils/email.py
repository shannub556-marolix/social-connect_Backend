# users/utils/email.py
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

def send_verification_email(user, token):
    verify_url = f"{settings.FRONTEND_URL}/auth/verify-email/?token={token}"
    subject = "Verify your SocialConnect account"
    message = f"Hi {user.username},\n\nClick the link to verify your account:\n{verify_url}\n\nIf you didn't create an account, ignore."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

def send_password_reset_email(user, token):
    reset_url = f"{settings.FRONTEND_URL}/auth/reset-password/?token={token}"
    subject = "Reset your SocialConnect password"
    message = f"Hi {user.username},\n\nUse the link to reset your password (valid for a few hours):\n{reset_url}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
