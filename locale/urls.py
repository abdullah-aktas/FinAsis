"""
Locale URLs
"""
from django.urls import path
from . import views

app_name = "locale"

urlpatterns = [
    path("set-language/", views.set_language, name="set_language"),
    path("set-language-compat/", views.set_language, name="set_language_compat"),
    path("translations/", views.get_translations, name="get_translations"),
    path("config/", views.get_language_config, name="get_config"),
    path("languages/", views.get_available_languages, name="get_languages"),
]
