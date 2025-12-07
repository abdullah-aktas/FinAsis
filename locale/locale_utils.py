"""
Locale Utilities for FinAsis
Çok Dilli Destek Yardımcı Fonksiyonları
"""

import json
from pathlib import Path
from django.utils.translation import get_language, activate
from typing import Dict, Any, Optional


class LocaleManager:
    """
    Çok dilli destek yöneticisi
    - JSON tabanlı frontend çevirileri
    - Django i18n entegrasyonu
    - RTL dil desteği
    """

    # Desteklenen diller
    SUPPORTED_LANGUAGES = {
        "tr": {"name": "Türkçe", "native": "Türkçe", "flag": "🇹🇷", "rtl": False},
        "en": {"name": "English", "native": "English", "flag": "🇬🇧", "rtl": False},
        "ar": {"name": "Arabic", "native": "العربية", "flag": "🇸🇦", "rtl": True},
        "ku": {"name": "Kurdish", "native": "کوردی", "flag": "☀️", "rtl": True},
        "de": {"name": "German", "native": "Deutsch", "flag": "🇩🇪", "rtl": False},
        "fr": {"name": "French", "native": "Français", "flag": "🇫🇷", "rtl": False},
    }

    # RTL Diller
    RTL_LANGUAGES = ["ar", "ku", "he", "fa", "ur"]

    @classmethod
    def get_locale_dir(cls) -> Path:
        """Locale klasörünün yolunu döndür"""
        return Path(__file__).parent

    @classmethod
    def load_translations(
        cls, lang_code: str, module: str = "common"
    ) -> Dict[str, Any]:
        """
        Belirli bir dil ve modül için çevirileri yükle

        Args:
            lang_code: Dil kodu (tr, en, ar, vb.)
            module: Modül adı (varsayılan: common, tüm çeviriler için)

        Returns:
            Çeviri sözlüğü
        """
        # JS klasöründeki kapsamlı çeviriler
        js_file = cls.get_locale_dir() / "js" / f"{lang_code}.json"

        if js_file.exists():
            with open(js_file, "r", encoding="utf-8") as f:
                translations = json.load(f)

                # Belirli bir modül isteniyorsa
                if module != "common" and module in translations:
                    return translations[module]

                return translations

        # Fallback: Ana klasördeki basit JSON
        simple_file = cls.get_locale_dir() / f"{lang_code}.json"
        if simple_file.exists():
            with open(simple_file, "r", encoding="utf-8") as f:
                return json.load(f)

        return {}

    @classmethod
    def get_translation(
        cls, key: str, lang_code: Optional[str] = None, default: str = ""
    ) -> str:
        """
        Belirli bir anahtar için çeviriyi getir

        Args:
            key: Çeviri anahtarı (örn: 'common.save', 'auth.login')
            lang_code: Dil kodu (None ise mevcut dil kullanılır)
            default: Bulunamazsa döndürülecek varsayılan değer

        Returns:
            Çevrilmiş metin
        """
        if not lang_code:
            lang_code = get_language() or "tr"

        # Anahtarı modül ve key'e ayır
        parts = key.split(".")

        if len(parts) >= 2:
            module = parts[0]
            key_path = parts[1:]
        else:
            module = "common"
            key_path = parts

        # Çevirileri yükle
        translations = cls.load_translations(lang_code, module)

        # İç içe key'leri takip et
        result = translations
        for part in key_path:
            if isinstance(result, dict) and part in result:
                result = result[part]
            else:
                return default or key

        return result if isinstance(result, str) else default or key

    @classmethod
    def is_rtl_language(cls, lang_code: str) -> bool:
        """Dil RTL mi kontrol et"""
        return lang_code in cls.RTL_LANGUAGES

    @classmethod
    def get_language_info(cls, lang_code: str) -> Dict[str, Any]:
        """Dil bilgilerini getir"""
        return cls.SUPPORTED_LANGUAGES.get(
            lang_code,
            {"name": lang_code, "native": lang_code, "flag": "🌐", "rtl": False},
        )

    @classmethod
    def get_all_languages(cls) -> Dict[str, Dict[str, Any]]:
        """Tüm desteklenen dilleri döndür"""
        return cls.SUPPORTED_LANGUAGES

    @classmethod
    def set_language(cls, lang_code: str, request=None) -> bool:
        """
        Aktif dili değiştir

        Args:
            lang_code: Dil kodu
            request: Django request objesi (session için)

        Returns:
            Başarılı ise True
        """
        if lang_code not in cls.SUPPORTED_LANGUAGES:
            return False

        # Django dilini aktif et
        activate(lang_code)

        # Session'a kaydet
        if request and hasattr(request, "session"):
            request.session["django_language"] = lang_code

        return True

    @classmethod
    def generate_frontend_config(cls, lang_code: str) -> Dict[str, Any]:
        """
        Frontend için dil konfigürasyonu oluştur

        Returns:
            Frontend'de kullanılacak config objesi
        """
        lang_info = cls.get_language_info(lang_code)
        translations = cls.load_translations(lang_code)

        return {
            "currentLanguage": lang_code,
            "languageInfo": lang_info,
            "rtl": lang_info.get("rtl", False),
            "translations": translations,
            "availableLanguages": cls.SUPPORTED_LANGUAGES,
        }


def t(key: str, lang_code: Optional[str] = None, default: str = "") -> str:
    """
    Kısa çeviri fonksiyonu

    Usage:
        from apps.locale.locale_utils import t

        translated = t('common.save')
        translated_en = t('auth.login', 'en')
    """
    return LocaleManager.get_translation(key, lang_code, default)


def get_locale_context(request) -> Dict[str, Any]:
    """
    Template context için locale bilgilerini hazırla

    Usage in views:
        context = get_locale_context(request)
    """
    lang_code = get_language() or "tr"
    lang_info = LocaleManager.get_language_info(lang_code)

    return {
        "LANGUAGE_CODE": lang_code,
        "LANGUAGE_INFO": lang_info,
        "RTL": lang_info.get("rtl", False),
        "AVAILABLE_LANGUAGES": LocaleManager.get_all_languages(),
        "locale_config": LocaleManager.generate_frontend_config(lang_code),
    }
