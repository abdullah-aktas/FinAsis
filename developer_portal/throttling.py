from __future__ import annotations

from rest_framework.throttling import SimpleRateThrottle

from developer_portal.models import DeveloperAPIKey


class DeveloperAPIKeyRateThrottle(SimpleRateThrottle):
    """
    API anahtarının planına göre dinamik hız limiti uygular.

    `settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']` içerisinde
    `developer_<plan>` formatında tanımlanmış değerleri kullanır.
    """

    scope = "developer_standard"

    def allow_request(self, request, view):
        api_key = self._get_api_key(request)
        if api_key is None:
            # API anahtarı olmayan istekler bu throttle'dan etkilenmez
            return True

        plan_scope = self._get_scope_for_plan(api_key.rate_limit_plan)
        self.scope = plan_scope
        self.rate = self.get_rate()
        if self.rate is None:
            # Konfigürasyon yapılmamışsa sınırsız olarak kabul et
            return True

        self.key = self.get_cache_key(request, view)
        if self.key is None:
            return True

        return super().allow_request(request, view)

    def get_cache_key(self, request, view):
        api_key = self._get_api_key(request)
        if api_key is None:
            return None

        ident = str(api_key.pk)
        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }

    @staticmethod
    def _get_api_key(request) -> DeveloperAPIKey | None:
        django_request = getattr(request, "_request", request)
        candidate = getattr(django_request, "_developer_api_key", None)
        if isinstance(candidate, DeveloperAPIKey):
            return candidate
        auth = getattr(django_request, "auth", None)
        if isinstance(auth, DeveloperAPIKey):
            return auth
        return None

    @staticmethod
    def _get_scope_for_plan(plan: str | None) -> str:
        sanitized = (plan or "standard").lower().replace(" ", "_")
        return f"developer_{sanitized}"


__all__ = ["DeveloperAPIKeyRateThrottle"]

