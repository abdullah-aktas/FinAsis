# -*- coding: utf-8 -*-
from django.utils import translation
from django.conf import settings
from .loader import language_loader

class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URL'den dil kodunu al
        lang_code = request.path.split('/')[1]
        
        # Eğer URL'de geçerli bir dil kodu yoksa
        if lang_code not in language_loader.get_available_languages():
            # Cookie'den dil kodunu al
            lang_code = request.COOKIES.get('django_language', settings.LANGUAGE_CODE)
            
            # Cookie'de de yoksa varsayılan dili kullan
            if lang_code not in language_loader.get_available_languages():
                lang_code = settings.LANGUAGE_CODE

        # Dili aktifleştir
        translation.activate(lang_code)
        request.LANGUAGE_CODE = lang_code

        response = self.get_response(request)
        
        # Dil tercihini cookie'ye kaydet
        response.set_cookie('django_language', lang_code)
        
        return response 