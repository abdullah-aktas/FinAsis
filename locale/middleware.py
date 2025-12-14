"""
Locale Middleware
RTL Dil Desteği ve Otomatik Dil Algılama
"""

from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from .locale_utils import LocaleManager


class LocaleMiddleware(MiddlewareMixin):
    """
    Çok dilli destek için middleware
    - Otomatik dil algılama
    - RTL HTML dir attribute
    - Request'e locale bilgisi ekleme
    """

    def process_request(self, request):
        """Request işleme"""
        # Mevcut dili al
        language = translation.get_language()

        if not language:
            language = "tr"  # Varsayılan dil

        # Request'e locale bilgilerini ekle
        request.LANGUAGE_CODE = language
        request.LANGUAGE_INFO = LocaleManager.get_language_info(language)
        request.IS_RTL = LocaleManager.is_rtl_language(language)

    def process_template_response(self, request, response):
        """Template response işleme"""
        # Context'e locale bilgilerini ekle
        if hasattr(response, "context_data") and response.context_data:
            language = getattr(request, "LANGUAGE_CODE", "tr")
            response.context_data["LANGUAGE_CODE"] = language
            response.context_data["LANGUAGE_INFO"] = getattr(
                request, "LANGUAGE_INFO", {}
            )
            response.context_data["IS_RTL"] = getattr(request, "IS_RTL", False)
            response.context_data["AVAILABLE_LANGUAGES"] = (
                LocaleManager.get_all_languages()
            )

        return response


class RTLMiddleware(MiddlewareMixin):
    """
    RTL Diller için otomatik HTML dir attribute ekleme
    """

    def process_response(self, request, response):
        """Response işleme"""
        # Sadece HTML response'lar için
        if "text/html" in response.get("Content-Type", ""):
            language = translation.get_language() or "tr"

            # RTL dil mi kontrol et
            if LocaleManager.is_rtl_language(language):
                # HTML içinde <html> tag'ini bul ve dir="rtl" ekle
                if hasattr(response, "content"):
                    content = response.content.decode("utf-8")

                    # <html> tag'ini değiştir
                    if "<html" in content and "dir=" not in content:
                        content = content.replace("<html", '<html dir="rtl"')
                        response.content = content.encode("utf-8")
                        response["Content-Length"] = len(response.content)

        return response
