# -*- coding: utf-8 -*-
"""
TradeSim Production Configuration
Canlı ortam için güvenlik ve performans ayarları
"""

# Production Security Settings
PRODUCTION_SECURITY = {
    "SECURE_SSL_REDIRECT": True,
    "SECURE_PROXY_SSL_HEADER": ("HTTP_X_FORWARDED_PROTO", "https"),
    "SECURE_HSTS_SECONDS": 31536000,
    "SECURE_HSTS_INCLUDE_SUBDOMAINS": True,
    "SECURE_HSTS_PRELOAD": True,
    "SECURE_CONTENT_TYPE_NOSNIFF": True,
    "SECURE_BROWSER_XSS_FILTER": True,
    "X_FRAME_OPTIONS": "DENY",
    "CSRF_COOKIE_SECURE": True,
    "SESSION_COOKIE_SECURE": True,
    "SECURE_REFERRER_POLICY": "strict-origin-when-cross-origin",
}

# TradeSim Game Settings
TRADESIM_SETTINGS = {
    "MAX_PLAYERS_PER_GAME": 10,
    "SESSION_TIMEOUT_MINUTES": 60,
    "MAX_INVENTORY_ITEMS": 50,
    "MAX_TRADE_AMOUNT": 1000000,
    "MARKET_UPDATE_INTERVAL_SECONDS": 300,  # 5 dakika
    "ENABLE_DEBUG_CONSOLE": False,  # Production'da kapatılacak
    "LOG_LEVEL": "INFO",
    "RATE_LIMIT_TRADES_PER_MINUTE": 10,
    "RATE_LIMIT_API_CALLS_PER_MINUTE": 60,
}

# Cache Settings for TradeSim
TRADESIM_CACHE = {
    "MARKETS_CACHE_TIMEOUT": 300,  # 5 dakika
    "CITIES_CACHE_TIMEOUT": 3600,  # 1 saat
    "PRODUCTS_CACHE_TIMEOUT": 3600,  # 1 saat
    "LEADERBOARD_CACHE_TIMEOUT": 600,  # 10 dakika
}

# Database Optimization
TRADESIM_DB_SETTINGS = {
    "USE_CONNECTION_POOLING": True,
    "MAX_CONNECTIONS": 20,
    "CONNECTION_TIMEOUT": 30,
    "ENABLE_QUERY_LOGGING": False,  # Production'da kapatılacak
}

# Monitoring and Logging
TRADESIM_MONITORING = {
    "ENABLE_METRICS": True,
    "ENABLE_ERROR_TRACKING": True,
    "LOG_TRADES": True,
    "LOG_USER_ACTIONS": True,
    "METRICS_RETENTION_DAYS": 30,
    "ERROR_LOG_RETENTION_DAYS": 90,
}

# API Rate Limiting
TRADESIM_RATE_LIMITS = {
    "trades": "10/minute",
    "market_data": "30/minute",
    "city_change": "5/minute",
    "session_start": "3/minute",
}

# Feature Flags
TRADESIM_FEATURES = {
    "ENABLE_AI_SUGGESTIONS": True,
    "ENABLE_TOURNAMENTS": True,
    "ENABLE_CHAT": True,
    "ENABLE_NOTIFICATIONS": True,
    "ENABLE_QR_REWARDS": True,
    "ENABLE_LEADERBOARDS": True,
    "ENABLE_ANALYTICS": True,
    "ENABLE_SOCIAL_FEATURES": True,
}

# Content Security Policy
CSP_SETTINGS = {
    "default-src": "'self'",
    "script-src": "'self' 'unsafe-inline' cdn.jsdelivr.net",
    "style-src": "'self' 'unsafe-inline' cdn.jsdelivr.net fonts.googleapis.com",
    "font-src": "'self' fonts.gstatic.com",
    "img-src": "'self' data: https:",
    "connect-src": "'self'",
    "frame-ancestors": "'none'",
    "base-uri": "'self'",
    "form-action": "'self'",
}

# CORS Settings (if needed for API)
CORS_SETTINGS = {
    "CORS_ALLOWED_ORIGINS": [
        "https://finasis.com",
        "https://www.finasis.com",
        "https://app.finasis.com",
    ],
    "CORS_ALLOW_CREDENTIALS": True,
    "CORS_PREFLIGHT_MAX_AGE": 86400,
}

# Health Check Endpoints
HEALTH_CHECK_ENDPOINTS = [
    "/health/",
    "/health/db/",
    "/health/cache/",
    "/health/tradesim/",
]

# Backup and Recovery
BACKUP_SETTINGS = {
    "ENABLE_AUTO_BACKUP": True,
    "BACKUP_INTERVAL_HOURS": 6,
    "BACKUP_RETENTION_DAYS": 30,
    "BACKUP_LOCATION": "s3://finasis-backups/tradesim/",
}

# Error Pages
ERROR_PAGES = {
    400: "errors/400.html",
    403: "errors/403.html",
    404: "errors/404.html",
    500: "errors/500.html",
    502: "errors/502.html",
    503: "errors/503.html",
}
