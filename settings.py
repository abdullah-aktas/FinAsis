# Analitik Modülü Ayarları
ANALYTICS_CACHE_TIMEOUT = 3600  # 1 saat
ANALYTICS_MAX_DATA_POINTS = 1000

# Rate Limiting
ANALYTICS_RATE_LIMIT = {
    'max_requests': 60,
    'time_window': 60  # saniye
}

# Widget Ayarları
ANALYTICS_WIDGET_SETTINGS = {
    'default_colors': {
        'primary': '#2193B0',
        'secondary': '#6DD5ED',
        'success': '#30B32D',
        'warning': '#FFDD00',
        'danger': '#F03E3E'
    },
    'chart_options': {
        'responsive': True,
        'maintainAspectRatio': False
    }
}

# Veri Kaynağı Ayarları
ANALYTICS_DATA_SOURCES = {
    'database': {
        'max_connections': 10,
        'timeout': 30  # saniye
    },
    'api': {
        'timeout': 10,  # saniye
        'retry_attempts': 3
    }
}

# Rapor Ayarları
ANALYTICS_REPORT_SETTINGS = {
    'max_rows': 10000,
    'export_formats': ['csv', 'excel', 'pdf'],
    'default_timezone': 'Europe/Istanbul'
}

# Middleware Ayarları
MIDDLEWARE = [
    # ... existing middleware ...
    'analytics.middleware.AnalyticsErrorMiddleware',
] 