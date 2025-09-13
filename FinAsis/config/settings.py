# Re-export settings from inner package for pytest-django
from FinAsis.config.settings import *  # noqa

# Ensure URL conf points to inner project
ROOT_URLCONF = 'FinAsis.config.urls'
