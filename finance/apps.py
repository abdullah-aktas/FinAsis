# -*- coding: utf-8 -*-
"""
FinAsis Finans modülü uygulaması
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FinanceConfig(AppConfig):
    """Finans uygulaması yapılandırması"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finance'
    verbose_name = _('Finans')
    label = 'finance'  # Benzersiz etiket
    
    def ready(self):
        """Uygulama başlatıldığında yapılacak işlemler"""
        import finance.signals  # noqa

    def get_urls(self):
        """
        Uygulama için URL yapılandırmasını döndürür.
        """
        from django.urls import path
        from . import views

        urlpatterns = [
            path('finance/', views.finance_view),
        ]
        return urlpatterns

    def get_model(self, model_name, require_ready=True):
        """
        Uygulama için belirtilen modeli döndürür.
        """
        return super().get_model(model_name, require_ready=require_ready)

    def get_models(self, include_auto_created=True, include_swapped=True):
        """
        Uygulama için model tanımlarını döndürür.
        """
        return self.models.values()

    def get_app_config(self):
        """
        Uygulama yapılandırmasını döndürür.
        """
        return self

    def get_app_name(self):
        """
        Uygulama adını döndürür.
        """
        return self.name

    def get_verbose_name(self):
        """
        Uygulama için açıklayıcı bir ad döndürür.
        """
        return self.verbose_name

    def get_label(self):
        """
        Uygulama için benzersiz bir etiket döndürür.
        """
        return self.label

    def get_app_configs(self):
        """
        Uygulama yapılandırmalarını döndürür.
        """
        return [self]

    def get_app_label(self):
        """
        Uygulama için etiket döndürür.
        """
        return self.label

    def get_app_dependencies(self):
        """
        Uygulama için bağımlı uygulamaları döndürür.
        """
        return []

    def get_app_module(self):
        """
        Uygulama modülünü döndürür.
        """
        return __import__(self.name)

    def get_app_path(self):
        """
        Uygulama dizinini döndürür.
        """
        from django.utils.module_loading import get_app_path
        return get_app_path(self.name)

    def get_app_template_dirs(self):
        """
        Uygulama için şablon dizinlerini döndürür.
        """
        from django.utils.module_loading import get_app_template_dirs
        return get_app_template_dirs(self.name)

    def get_app_template_name(self, template_name):
        """
        Uygulama için belirtilen şablonun adını döndürür.
        """
        from django.utils.module_loading import get_app_template_name
        return get_app_template_name(self.name, template_name)