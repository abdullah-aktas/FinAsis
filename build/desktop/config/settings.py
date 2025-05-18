# -*- coding: utf-8 -*-
# API Keys
OPENWEATHER_API_KEY = env('OPENWEATHER_API_KEY', default='')
ALPHA_VANTAGE_API_KEY = env('ALPHA_VANTAGE_API_KEY', default='')

# Cache settings for API responses
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache timeouts
WEATHER_CACHE_TIMEOUT = 30 * 60  # 30 minutes
FINANCE_CACHE_TIMEOUT = 15 * 60  # 15 minutes 