from __future__ import annotations

from typing import Optional

from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from developer_portal.services import key_manager


class APIKeyAuthentication(BaseAuthentication):
    """
    `ApiKey` yetkilendirme şemasını destekler.

    Header öncelikleri:
        - `Authorization: ApiKey <prefix.secret>`
        - `X-API-Key: <prefix.secret>`
    """

    keyword = "ApiKey"
    header_name = "HTTP_X_API_KEY"

    def authenticate(self, request):
        raw_key = self._get_key_from_request(request)
        if not raw_key:
            return None

        api_key = key_manager.verify_raw_key(raw_key)
        if api_key is None:
            raise AuthenticationFailed(
                _("Geçersiz veya devre dışı bırakılmış API anahtarı.")
            )

        if api_key.is_expired:
            raise AuthenticationFailed(_("API anahtarının süresi dolmuş."))

        if api_key.allowed_ips:
            client_ip = self._get_client_ip(request)
            if client_ip not in api_key.allowed_ips:
                raise AuthenticationFailed(_("Bu IP adresi için yetki bulunmuyor."))

        # DRF Request nesnesi -> orijinal WSGIRequest üzerinde attribütleri sakla.
        django_request = getattr(request, "_request", request)
        setattr(django_request, "_developer_api_key", api_key)

        return api_key.owner, api_key

    # ------------------------------------------------------------------ helpers
    def _get_key_from_request(self, request) -> Optional[str]:
        auth = get_authorization_header(request).decode("utf-8").strip()
        if auth:
            parts = auth.split()
            if len(parts) == 2 and parts[0] == self.keyword:
                return parts[1]

        header_key = request.META.get(self.header_name)
        if header_key:
            return header_key.strip()
        return None

    @staticmethod
    def _get_client_ip(request) -> str | None:
        django_request = getattr(request, "_request", request)
        meta = getattr(django_request, "META", {})
        forwarded = meta.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            # İlk IP'yi kullan
            return forwarded.split(",")[0].strip()
        return meta.get("REMOTE_ADDR")


__all__ = ["APIKeyAuthentication"]
