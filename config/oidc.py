"""
OIDC/Keycloak entegrasyon ayarları.

Bu dosya ortam değişkenlerine duyarlı olacak şekilde Keycloak client ayarlarını tutar.
"""

from __future__ import annotations

import os

OIDC_ENABLED = os.getenv("OIDC_ENABLED", "false").lower() in {"1", "true", "yes"}

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "https://sso.finasis.com")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "finasis")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "finasis-web")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")
KEYCLOAK_AUTHORITY = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}"

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/accounts/profile/"
LOGOUT_REDIRECT_URL = "/"
