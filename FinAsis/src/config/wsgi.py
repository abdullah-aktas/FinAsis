"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Normalized settings module path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.config.settings')

application = get_wsgi_application()
