"""
Locale Views for Language Switching
Dil Değiştirme View'ları
"""
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import translation
from django.conf import settings
from .locale_utils import LocaleManager

# Session key for language preference
LANGUAGE_SESSION_KEY = "_language"


@require_http_methods(["POST", "GET"])
def set_language(request):
    """
    Dil değiştirme endpoint'i

    Usage:
        POST /locale/set-language/
        {
            "language": "en"
        }

        veya

        GET /locale/set-language/?language=en&next=/dashboard/
    """
    # GET veya POST ile dil kodunu al
    if request.method == "POST":
        lang_code = request.POST.get("language") or request.POST.get("lang")
    else:
        lang_code = request.GET.get("language") or request.GET.get("lang")

    # Geçerli dil mi kontrol et
    if lang_code and lang_code in dict(settings.LANGUAGES):
        # Dili aktif et
        translation.activate(lang_code)

        # Session'a kaydet
        request.session[LANGUAGE_SESSION_KEY] = lang_code

        # Cookie'ye de kaydet
        response_data = {
            "success": True,
            "language": lang_code,
            "message": f"Dil {lang_code} olarak değiştirildi",
        }

        # AJAX request ise JSON dön
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            response = JsonResponse(response_data)
        else:
            # Normal request ise redirect et
            next_url = (
                request.POST.get("next")
                or request.GET.get("next")
                or request.META.get("HTTP_REFERER", "/")
            )
            response = redirect(next_url)

        # Cookie set et
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            lang_code,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
        )

        return response

    # Geçersiz dil kodu
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {"success": False, "error": "Invalid language code"}, status=400
        )

    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_http_methods(["GET"])
def get_translations(request):
    """
    Frontend için çevirileri JSON olarak döndür

    Usage:
        GET /locale/translations/?lang=tr&module=common
    """
    lang_code = request.GET.get("lang") or translation.get_language() or "tr"
    module = request.GET.get("module", "common")

    translations = LocaleManager.load_translations(lang_code, module)

    return JsonResponse(
        {
            "success": True,
            "language": lang_code,
            "module": module,
            "translations": translations,
        }
    )


@require_http_methods(["GET"])
def get_language_config(request):
    """
    Frontend için tam dil konfigürasyonu

    Usage:
        GET /locale/config/
    """
    lang_code = translation.get_language() or "tr"
    config = LocaleManager.generate_frontend_config(lang_code)

    return JsonResponse({"success": True, "config": config})


@require_http_methods(["GET"])
def get_available_languages(request):
    """
    Mevcut dillerin listesini döndür

    Usage:
        GET /locale/languages/
    """
    languages = LocaleManager.get_all_languages()
    current_lang = translation.get_language() or "tr"

    return JsonResponse(
        {"success": True, "currentLanguage": current_lang, "languages": languages}
    )
