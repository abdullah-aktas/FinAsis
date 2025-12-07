"""
Pytest configuration for FinAsis project.
This file ensures proper Django setup and prevents module conflicts.
"""

import os

# Set DISABLE_LOCALE_APP before Django settings are loaded
# This prevents the conflict between Python's standard 'locale' module
# and Django's 'locale' app
# This must be set BEFORE any Django imports
if "DISABLE_LOCALE_APP" not in os.environ:
    os.environ["DISABLE_LOCALE_APP"] = "1"

# Ensure pytest-django is configured before Django setup
pytest_plugins = ["pytest_django"]
