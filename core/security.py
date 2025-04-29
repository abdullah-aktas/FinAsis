# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import qrcode
import io
import base64
from cryptography.fernet import Fernet
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class TwoFactorAuth:
    @staticmethod
    def generate_secret_key():
        return get_random_string(32)

    @staticmethod
    def generate_qr_code(secret_key, username):
        qr = qrcode.make(f'otpauth://totp/{username}?secret={secret_key}')
        buffer = io.BytesIO()
        qr.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()

class EncryptionService:
    def __init__(self):
        self.key = settings.ENCRYPTION_KEY
        self.cipher_suite = Fernet(self.key)

    def encrypt(self, data):
        return self.cipher_suite.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data):
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()

class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Güvenlik başlıkları ekle
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Content-Security-Policy'] = "default-src 'self'"
        
        return response

class AuditLog:
    @staticmethod
    def log_security_event(user, event_type, details):
        logger.info(f"Security Event - User: {user}, Type: {event_type}, Details: {details}")

class RateLimiter:
    def __init__(self, key, limit, period):
        self.key = key
        self.limit = limit
        self.period = period

    def is_allowed(self):
        current = cache.get(self.key, 0)
        if current >= self.limit:
            return False
        cache.incr(self.key)
        cache.set(self.key, current + 1, self.period)
        return True

class SecurityView(LoginRequiredMixin, View):
    def get(self, request):
        two_factor = TwoFactorAuth()
        secret_key = two_factor.generate_secret_key()
        qr_code = two_factor.generate_qr_code(secret_key, request.user.username)
        
        context = {
            'qr_code': qr_code,
            'secret_key': secret_key,
        }
        return render(request, 'security/settings.html', context)

    def post(self, request):
        # İki faktörlü doğrulama ayarlarını kaydet
        secret_key = request.POST.get('secret_key')
        request.user.profile.two_factor_secret = secret_key
        request.user.profile.save()
        
        messages.success(request, 'İki faktörlü doğrulama başarıyla ayarlandı.')
        return JsonResponse({'status': 'success'}) 