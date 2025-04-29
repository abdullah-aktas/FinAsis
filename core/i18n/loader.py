# -*- coding: utf-8 -*-
import json
import os
from django.conf import settings

class LanguageLoader:
    def __init__(self):
        self.translations = {}
        self.load_all_translations()

    def load_all_translations(self):
        """Tüm dil dosyalarını yükler"""
        locale_dir = os.path.join(settings.BASE_DIR, 'locale')
        for filename in os.listdir(locale_dir):
            if filename.endswith('.json'):
                lang_code = filename[:-5]  # .json uzantısını kaldır
                file_path = os.path.join(locale_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)

    def get_translation(self, lang_code, key):
        """Belirtilen dil ve anahtar için çeviriyi döndürür"""
        if lang_code not in self.translations:
            return key
        return self.translations[lang_code].get(key, key)

    def get_available_languages(self):
        """Mevcut dillerin listesini döndürür"""
        return list(self.translations.keys())

# Singleton instance
language_loader = LanguageLoader() 