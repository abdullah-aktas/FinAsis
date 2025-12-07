# -*- coding: utf-8 -*-
"""
TradeSim Error Handlers
Production için güvenli hata yönetimi
"""
from django.http import JsonResponse
from django.shortcuts import render
import logging

logger = logging.getLogger("tradesim")


def production_error_handler(func):
    """Production ortamında hataları güvenli şekilde yakalar"""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log the error
            logger.error(f"TradeSim Error in {func.__name__}: {str(e)}", exc_info=True)

            # Return safe error response
            if hasattr(args[0], "META") and "application/json" in args[0].META.get(
                "HTTP_ACCEPT", ""
            ):
                return JsonResponse(
                    {
                        "success": False,
                        "error": "Bir hata oluştu. Lütfen tekrar deneyin.",
                        "error_code": "INTERNAL_ERROR",
                    },
                    status=500,
                )
            else:
                return render(
                    args[0],
                    "trade_sim/error.html",
                    {
                        "error_message": "Oyunda teknik bir sorun oluştu. Lütfen sayfayı yenileyip tekrar deneyin.",
                        "error_code": "GAME_ERROR",
                    },
                )

    return wrapper


def validate_game_request(func):
    """Oyun isteklerini doğrular"""

    def wrapper(request, *args, **kwargs):
        # Rate limiting check
        from django.core.cache import cache

        user_key = f"rate_limit_{request.user.id if request.user.is_authenticated else request.META.get('REMOTE_ADDR')}"
        current_requests = cache.get(user_key, 0)

        if current_requests > 60:  # Max 60 request per minute
            return JsonResponse(
                {
                    "success": False,
                    "error": "Çok fazla istek gönderdiniz. Lütfen bir dakika bekleyin.",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                },
                status=429,
            )

        cache.set(user_key, current_requests + 1, 60)

        # Session validation
        if request.user.is_authenticated:
            session = request.session.get("tradesim_game_session")
            if not session:
                return JsonResponse(
                    {
                        "success": False,
                        "error": "Oyun oturumu bulunamadı. Lütfen oyunu yeniden başlatın.",
                        "error_code": "SESSION_REQUIRED",
                    },
                    status=401,
                )

        return func(request, *args, **kwargs)

    return wrapper


def log_game_action(action_type, user, details=None):
    """Oyun aksiyonlarını loglar"""
    logger.info(
        f"TradeSim Action: {action_type} by user {user.id if user.is_authenticated else 'anonymous'}",
        extra={
            "action_type": action_type,
            "user_id": user.id if user.is_authenticated else None,
            "details": details or {},
        },
    )


class TradeSim404Handler:
    """TradeSim 404 sayfaları için özel handler"""

    @staticmethod
    def handle_404(request, exception=None):
        return render(
            request,
            "trade_sim/404.html",
            {
                "error_message": "Aradığınız sayfa bulunamadı.",
                "return_url": "/games/trade-sim/start/",
            },
            status=404,
        )


class TradeSim500Handler:
    """TradeSim 500 sayfaları için özel handler"""

    @staticmethod
    def handle_500(request):
        return render(
            request,
            "trade_sim/500.html",
            {
                "error_message": "Teknik bir sorun oluştu. Ekibimiz bilgilendirildi.",
                "return_url": "/games/trade-sim/start/",
            },
            status=500,
        )


def validate_trade_data(data):
    """Ticaret verilerini doğrular"""
    required_fields = ["action", "item_name", "amount", "price"]

    for field in required_fields:
        if field not in data:
            raise ValueError(f"Eksik alan: {field}")

    # Amount validation
    try:
        amount = float(data["amount"])
        if amount <= 0 or amount > 1000000:
            raise ValueError("Geçersiz miktar")
    except (ValueError, TypeError):
        raise ValueError("Miktar sayısal olmalıdır")

    # Price validation
    try:
        price = float(data["price"])
        if price <= 0 or price > 10000000:
            raise ValueError("Geçersiz fiyat")
    except (ValueError, TypeError):
        raise ValueError("Fiyat sayısal olmalıdır")

    # Action validation
    if data["action"] not in ["buy", "sell"]:
        raise ValueError("Geçersiz işlem tipi")

    return True


def sanitize_user_input(data):
    """Kullanıcı girdilerini temizler"""
    import re

    if isinstance(data, str):
        # Remove potentially dangerous characters
        data = re.sub(r'[<>"\'\\/]', "", data)
        # Limit length
        data = data[:100]
    elif isinstance(data, dict):
        return {k: sanitize_user_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_user_input(item) for item in data]

    return data
