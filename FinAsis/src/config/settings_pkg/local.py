from .base import *  # noqa

DEBUG = True

# Allow Django test client and local tools using default host
ALLOWED_HOSTS = list(globals().get('ALLOWED_HOSTS', []))
if 'testserver' not in ALLOWED_HOSTS:
	ALLOWED_HOSTS.append('testserver')
