# =============================================================================
# Production Settings for 50,000 Concurrent Users
# =============================================================================
"""
Production-specific settings for high-traffic deployment.
This file should be imported in the main settings file when DEBUG=False.
"""
from .base import *  # noqa: F403, F405

# =============================================================================
# Security Settings
# =============================================================================
DEBUG = False
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# =============================================================================
# Database Optimization (50K Users)
# =============================================================================
# Connection pooling for high concurrency
DATABASES["default"]["CONN_MAX_AGE"] = int(  # noqa: F405
    ENV("DJANGO_DB_CONN_MAX_AGE", "600")  # noqa: F405
)  # 10 minutes

# PostgreSQL-specific optimizations
if DATABASES["default"]["ENGINE"].endswith("postgresql"):  # noqa: F405
    DATABASES["default"]["OPTIONS"] = {  # noqa: F405
        **DATABASES["default"].get("OPTIONS", {}),  # noqa: F405
        "connect_timeout": 10,
        "options": "-c statement_timeout=30000 -c idle_in_transaction_session_timeout=30000",
    }

# =============================================================================
# Redis Cache Configuration (50K Users)
# =============================================================================
try:
    import django_redis  # noqa: F401

    REDIS_HOST = ENV("REDIS_HOST", "localhost")  # noqa: F405
    REDIS_PORT = int(ENV("REDIS_PORT", "6379"))  # noqa: F405
    REDIS_DB = int(ENV("REDIS_DB", "1"))  # noqa: F405
    REDIS_PASSWORD = ENV("REDIS_PASSWORD", "")  # noqa: F405

    REDIS_URL = "redis://"
    if REDIS_PASSWORD:
        REDIS_URL += f":{REDIS_PASSWORD}@"
    REDIS_URL += f"{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "PARSER_CLASS": "redis.connection.HiredisParser",
                "CONNECTION_POOL_KWARGS": {
                    "max_connections": 50,
                    "retry_on_timeout": True,
                    "socket_keepalive": True,
                    "socket_keepalive_options": {},
                },
                "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
                "IGNORE_EXCEPTIONS": True,  # Don't break if Redis is down
            },
            "KEY_PREFIX": "finasis",
            "TIMEOUT": int(
                ENV("CACHE_TIMEOUT", "300")
            ),  # 5 minutes default  # noqa: F405
        }
    }

    # Session backend - use Redis for sessions
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"
    SESSION_COOKIE_AGE = 43200  # 12 hours

except ImportError:
    # Fallback to local memory cache if django-redis is not available
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "finasis-cache",
        }
    }

# =============================================================================
# Channel Layers (WebSocket) - Redis Backend
# =============================================================================
try:
    import channels_redis  # noqa: F401

    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [(REDIS_HOST, REDIS_PORT)],
                "capacity": 1500,  # Max messages per channel
                "expiry": 10,  # Message expiry in seconds
            },
        },
    }
except ImportError:
    # Fallback to in-memory channel layer
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        },
    }

# =============================================================================
# Static & Media Files (Cloud Storage + CDN)
# =============================================================================
# Static files should be served via CDN in production
STATIC_URL = ENV("STATIC_URL", "/static/")  # noqa: F405
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405

# Media files - Cloud Storage
MEDIA_URL = ENV("MEDIA_URL", "/media/")  # noqa: F405
MEDIA_ROOT = BASE_DIR / "media"  # noqa: F405

# =============================================================================
# Logging Configuration (Production)
# =============================================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {name} {process:d} {thread:d} | {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": "common.logging.JsonFormatter",
        },
    },
    "filters": {
        "mask_pii": {
            "()": "common.logging.PIIMaskFilter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "filters": ["mask_pii"],
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "WARNING",  # Don't log all SQL queries in production
            "propagate": False,
        },
        "finasis": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# =============================================================================
# Performance Optimizations
# =============================================================================
# Disable admin documentation in production
ADMIN_DOCS = False

# Template caching
TEMPLATES[0]["OPTIONS"]["loaders"] = [  # noqa: F405
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    ),
]

# =============================================================================
# Email Configuration (Production)
# =============================================================================
EMAIL_BACKEND = ENV(  # noqa: F405
    "DJANGO_EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = ENV("DJANGO_EMAIL_HOST", "smtp.gmail.com")  # noqa: F405
EMAIL_PORT = int(ENV("DJANGO_EMAIL_PORT", "587"))  # noqa: F405
EMAIL_USE_TLS = env_bool("DJANGO_EMAIL_USE_TLS", True)  # noqa: F405
EMAIL_HOST_USER = ENV("DJANGO_EMAIL_HOST_USER", "")  # noqa: F405
EMAIL_HOST_PASSWORD = ENV("DJANGO_EMAIL_HOST_PASSWORD", "")  # noqa: F405
DEFAULT_FROM_EMAIL = ENV(  # noqa: F405
    "DJANGO_DEFAULT_FROM_EMAIL", "FinAsis <noreply@finasis.com.tr>"
)

# =============================================================================
# Monitoring & Observability
# =============================================================================
# Enable structured logging
ENABLE_STRUCTURED_LOGS = env_bool("ENABLE_STRUCTURED_LOGS", True)  # noqa: F405

# Sentry (if configured)
SENTRY_DSN = ENV("SENTRY_DSN", "")  # noqa: F405
if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        from sentry_sdk.integrations.redis import RedisIntegration

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[
                DjangoIntegration(transaction_style="url"),
                RedisIntegration(),
            ],
            traces_sample_rate=float(  # noqa: F405
                ENV("SENTRY_TRACES_SAMPLE_RATE", "0.1")  # noqa: F405
            ),  # 10% of transactions
            profiles_sample_rate=float(
                ENV("SENTRY_PROFILES_SAMPLE_RATE", "0.0")
            ),  # noqa: F405
            send_default_pii=False,
            environment=ENV("SENTRY_ENVIRONMENT", "production"),  # noqa: F405
        )
    except ImportError:
        pass

# =============================================================================
# Rate Limiting (50K Users)
# =============================================================================
# Increase rate limits for production
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {  # noqa: F405
    "developer_freemium": "500/day",  # Increased from 120
    "developer_standard": "5000/hour",  # Increased from 1000
    "developer_professional": "20000/hour",  # Increased from 5000
    "developer_enterprise": "100000/hour",  # Increased from 20000
}

# =============================================================================
# Security Headers
# =============================================================================
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# =============================================================================
# Allowed Hosts (Production)
# =============================================================================
# Cloud Run host will be added automatically via CLOUD_RUN_HOST env var
# See base.py for implementation
