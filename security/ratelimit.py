# -*- coding: utf-8 -*-
"""
Rate Limiting Decorators
API endpoint ve view'lar için rate limiting dekoratörleri
"""

from functools import wraps
from django_ratelimit.decorators import ratelimit
from django.conf import settings


def rate_limit_login(fn):
    """
    Login endpoint için rate limiting
    5 başarısız deneme / dakika
    """
    return ratelimit(
        key='ip',
        rate='5/m',
        method='POST',
        block=True
    )(fn)


def rate_limit_api_user(fn):
    """
    Authenticated kullanıcılar için API rate limiting
    100 istek / dakika
    """
    return ratelimit(
        key='user',
        rate='100/m',
        method=ratelimit.ALL,
        block=True
    )(fn)


def rate_limit_api_anon(fn):
    """
    Anonymous kullanıcılar için API rate limiting
    20 istek / dakika
    """
    return ratelimit(
        key='ip',
        rate='20/m',
        method=ratelimit.ALL,
        block=True
    )(fn)


def rate_limit_registration(fn):
    """
    Kayıt endpoint için rate limiting
    3 kayıt / saat / IP
    """
    return ratelimit(
        key='ip',
        rate='3/h',
        method='POST',
        block=True
    )(fn)


def rate_limit_password_reset(fn):
    """
    Şifre sıfırlama için rate limiting
    3 istek / saat
    """
    return ratelimit(
        key='ip',
        rate='3/h',
        method='POST',
        block=True
    )(fn)


def rate_limit_file_upload(fn):
    """
    Dosya yükleme için rate limiting
    10 dosya / dakika
    """
    return ratelimit(
        key='user_or_ip',
        rate='10/m',
        method='POST',
        block=True
    )(fn)


def rate_limit_search(fn):
    """
    Arama endpoint için rate limiting
    30 arama / dakika
    """
    return ratelimit(
        key='user_or_ip',
        rate='30/m',
        method='GET',
        block=True
    )(fn)


def rate_limit_payment(fn):
    """
    Ödeme endpoint için rate limiting
    5 ödeme / dakika (şüpheli aktivite engelleme)
    """
    return ratelimit(
        key='user',
        rate='5/m',
        method='POST',
        block=True
    )(fn)


def rate_limit_ai_assistant(fn):
    """
    AI Assistant endpoint için rate limiting
    20 istek / dakika (maliyetli işlemler)
    """
    return ratelimit(
        key='user',
        rate='20/m',
        method='POST',
        block=True
    )(fn)


def rate_limit_report_generation(fn):
    """
    Rapor oluşturma için rate limiting
    10 rapor / dakika (kaynak yoğun işlemler)
    """
    return ratelimit(
        key='user',
        rate='10/m',
        method='POST',
        block=True
    )(fn)


def adaptive_rate_limit(user_rate='100/m', anon_rate='20/m'):
    """
    Kullanıcı durumuna göre adaptif rate limiting
    
    Args:
        user_rate: Authenticated kullanıcılar için rate
        anon_rate: Anonymous kullanıcılar için rate
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                # Authenticated kullanıcı
                limited_fn = ratelimit(
                    key='user',
                    rate=user_rate,
                    method=ratelimit.ALL,
                    block=True
                )(fn)
            else:
                # Anonymous kullanıcı
                limited_fn = ratelimit(
                    key='ip',
                    rate=anon_rate,
                    method=ratelimit.ALL,
                    block=True
                )(fn)
            
            return limited_fn(request, *args, **kwargs)
        return wrapper
    return decorator


# DRF için custom throttle sınıfları
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class BurstUserThrottle(UserRateThrottle):
    """
    Authenticated kullanıcılar için kısa süreli burst koruması
    """
    scope = 'burst'
    rate = '30/min'


class SustainedUserThrottle(UserRateThrottle):
    """
    Authenticated kullanıcılar için uzun süreli limit
    """
    scope = 'sustained'
    rate = '1000/hour'


class BurstAnonThrottle(AnonRateThrottle):
    """
    Anonymous kullanıcılar için kısa süreli burst koruması
    """
    scope = 'burst_anon'
    rate = '10/min'


class StrictAnonThrottle(AnonRateThrottle):
    """
    Hassas endpoint'ler için sıkı anonymous throttling
    """
    scope = 'strict_anon'
    rate = '5/min'


class PaymentThrottle(UserRateThrottle):
    """
    Ödeme işlemleri için özel throttling
    """
    scope = 'payment'
    rate = '5/min'


class AIAssistantThrottle(UserRateThrottle):
    """
    AI Assistant için özel throttling (maliyetli işlemler)
    """
    scope = 'ai_assistant'
    rate = '20/min'
