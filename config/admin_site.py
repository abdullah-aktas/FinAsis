# -*- coding: utf-8 -*-
"""
FinAsis Admin Site Customization
Dinamik modül yönetimi ve yönlendirme desteği
"""
from django.contrib import admin
from django.urls import reverse, NoReverseMatch
from django.utils.translation import gettext_lazy as _
from django.apps import apps as django_apps
from django.utils.html import format_html


class FinAsisAdminSite(admin.AdminSite):
    """Özelleştirilmiş FinAsis Admin Site"""

    site_title = _("FinAsis Yönetim Paneli")
    site_header = _("FinAsis Finansal Yönetim")
    index_title = _("Modül Yönetim Paneli")

    def __init__(self, name="admin"):
        super().__init__(name)
        self._module_links = {}
        self._setup_module_links()

    def _setup_module_links(self):
        """Modül URL'lerini yapılandır"""
        self._module_links = {
            "accounts": "/accounts/",
            "accounting": "/accounting/",
            "finance": "/finance/",
            "finance_accounting": "/finance/accounting/",
            "billing": "/billing/",
            "education": "/education/",
            "games": "/games/",
            "ai_assistant": "/ai-assistant/",
            "blockchain": "/blockchain/",
            "advisors": "/advisors/",
            "management": "/management/",
            "permissions": "/permissions/",
            "security": "/security/",
            "tenancy": "/tenancy/",
            "submissions": "/submissions/",
            "developer_portal": "/developers/",
            "partners": "/partners/",
            "corporate": "/corporate/",
            "core_ui": "/",
            "common": "/common/",
            "kobi_analysis": "/kobi-analysis/",
            "virtual_company": "/virtual-company/",
        }

    def get_app_list(self, request):
        """
        Admin panelinde gösterilecek uygulamaları modül linkleriyle zenginleştir
        Modüllere tıklanınca o ekrana yönlendirme ekle
        """
        app_list = super().get_app_list(request)

        for app in app_list:
            app_label = app.get("app_label", "")
            app_url = self._module_links.get(app_label)

            if app_url:
                app["app_url"] = app_url
                # Modül adına link ekle
                app["module_link"] = format_html(
                    '<a href="{}" class="module-link" target="_blank">🔗 Modüle Git</a>',
                    app_url,
                )

            # Her model için de modül linki ekle
            for model in app.get("models", []):
                # Model için özel URL varsa ekle
                if app_url:
                    model["module_url"] = app_url

        return app_list

    def index(self, request, extra_context=None):
        """
        Admin ana sayfasını modül kartlarıyla zenginleştir
        Modüllere tıklanınca o ekrana yönlendirme
        """
        extra_context = extra_context or {}

        # URL'leri güvenli bir şekilde hazırla
        try:
            customer_add_url = reverse("admin:accounting_customer_add")
        except NoReverseMatch:
            customer_add_url = None

        try:
            modules_overview_url = reverse("admin:modules_overview")
        except NoReverseMatch:
            modules_overview_url = None

        extra_context["customer_add_url"] = customer_add_url
        extra_context["modules_overview_url"] = modules_overview_url

        # Önce varsayılan index'i çağır
        response = super().index(request, extra_context)

        # Eğer TemplateResponse ise, context'e modül bilgilerini ekle
        if hasattr(response, "context_data"):
            context = response.context_data
        else:
            context = extra_context

        # Modül listesi oluştur (sadece bir kez)
        if "modules" not in context:
            modules = []
            try:
                for app_config in django_apps.get_app_configs():
                    # Django core uygulamalarını atla
                    if app_config.name.startswith(
                        "django."
                    ) or app_config.name.startswith("rest_framework"):
                        continue

                    app_label = app_config.label
                    app_url = self._module_links.get(app_label)

                    # Model sayıları
                    model_count = 0
                    model_list = []
                    for model in app_config.get_models():
                        try:
                            count = model.objects.count()
                            model_count += count

                            # Admin'de kayıtlı modeller için link oluştur
                            try:
                                admin_url = reverse(
                                    f"admin:{model._meta.app_label}_{model._meta.model_name}_changelist"
                                )
                                model_list.append(
                                    {
                                        "name": model._meta.verbose_name_plural
                                        or model._meta.verbose_name,
                                        "count": count,
                                        "url": admin_url,
                                    }
                                )
                            except NoReverseMatch:
                                pass
                        except Exception:
                            pass

                    modules.append(
                        {
                            "label": app_label,
                            "name": getattr(app_config, "verbose_name", None)
                            or app_label.replace("_", " ").title(),
                            "url": app_url,
                            "model_count": model_count,
                            "models": model_list[:5],  # İlk 5 model
                        }
                    )

                # Modülleri alfabetik sırala
                modules.sort(key=lambda x: x["name"])
                context["modules"] = modules
                context["module_links"] = self._module_links
            except Exception:
                # Hata durumunda boş liste
                context["modules"] = []
                context["module_links"] = {}

        if hasattr(response, "context_data"):
            response.context_data.update(context)

        return response

    def each_context(self, request):
        """Her sayfada kullanılacak context"""
        context = super().each_context(request)
        context["finasis_logo"] = "/static/common/FinAsis_logo.png"
        context["finasis_desc"] = _("Modern Finansal Yönetim Platformu")

        # Kullanıcı bilgisi (Django'nun varsayılan context processor'ından gelir)
        # Ama açıkça ekleyelim ki template'lerde {{user}} kullanılabilsin
        if hasattr(request, "user"):
            context["user"] = request.user

            # Kullanıcının şirketini al
            # CustomUser modelinde company ForeignKey var
            try:
                if hasattr(request.user, "company") and request.user.company:
                    context["company"] = request.user.company
                else:
                    context["company"] = None
            except Exception:
                # Hata durumunda None
                context["company"] = None
        else:
            context["user"] = None
            context["company"] = None

        return context


# Özelleştirilmiş admin site oluştur
admin_site = FinAsisAdminSite(name="admin")

# NOT: Admin kayıtları common/apps.py'deki ready() metodunda kopyalanacak
# Bu sayede tüm uygulamalar yüklendikten sonra kayıtlar taşınır
