"""
Template Tags for Locale
Çeviri için Template Tag'leri
"""
from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from ..locale_utils import LocaleManager, t as translate

register = template.Library()


@register.simple_tag
def t(key, lang=None, default=''):
    """
    Template içinde çeviri yapmak için
    
    Usage:
        {% load locale_tags %}
        {% t 'common.save' %}
        {% t 'auth.login' 'en' %}
    """
    return translate(key, lang, default)


@register.simple_tag
def current_language():
    """Mevcut dili döndür"""
    return get_language() or 'tr'


@register.simple_tag
def is_rtl():
    """Mevcut dil RTL mi?"""
    lang = get_language() or 'tr'
    return LocaleManager.is_rtl_language(lang)


@register.simple_tag
def language_name(lang_code=None):
    """Dil adını döndür"""
    if not lang_code:
        lang_code = get_language() or 'tr'
    
    info = LocaleManager.get_language_info(lang_code)
    return info.get('name', lang_code)


@register.simple_tag
def language_native_name(lang_code=None):
    """Dilin kendi dilindeki adını döndür"""
    if not lang_code:
        lang_code = get_language() or 'tr'
    
    info = LocaleManager.get_language_info(lang_code)
    return info.get('native', lang_code)


@register.simple_tag
def language_flag(lang_code=None):
    """Dil bayrağını döndür"""
    if not lang_code:
        lang_code = get_language() or 'tr'
    
    info = LocaleManager.get_language_info(lang_code)
    return info.get('flag', '🌐')


@register.simple_tag
def available_languages():
    """Tüm mevcut dilleri döndür"""
    return LocaleManager.get_all_languages()


@register.inclusion_tag('locale/language_selector.html', takes_context=True)
def language_selector(context, style='dropdown'):
    """
    Dil seçici component
    
    Usage:
        {% load locale_tags %}
        {% language_selector %}
        {% language_selector 'flags' %}
    """
    request = context.get('request')
    current_lang = get_language() or 'tr'
    languages = LocaleManager.get_all_languages()
    
    return {
        'current_language': current_lang,
        'current_language_info': LocaleManager.get_language_info(current_lang),
        'languages': languages,
        'style': style,
        'request': request
    }


@register.filter
def translate_key(key, lang=None):
    """
    Filter olarak çeviri
    
    Usage:
        {{ 'common.save'|translate_key }}
        {{ 'auth.login'|translate_key:'en' }}
    """
    return translate(key, lang)


@register.simple_tag
def locale_js_config():
    """
    JavaScript için locale config oluştur
    
    Usage:
        {% load locale_tags %}
        <script>
            window.LOCALE_CONFIG = {% locale_js_config %};
        </script>
    """
    lang = get_language() or 'tr'
    config = LocaleManager.generate_frontend_config(lang)
    
    import json
    return mark_safe(json.dumps(config))

