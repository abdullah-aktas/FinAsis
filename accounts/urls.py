from django.urls import path, include, reverse_lazy
from django.views.generic import RedirectView
from . import views, views_mfa, views_auth
from .api import UserProfileView, CompanyView, AchievementsView, UserSettingsView
from .api_panel import panel_data_api
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.auth import views as auth_views
from security.ratelimit import rate_limit_login

app_name = "accounts"

# URL reverse helpers for maintainability
# Use reverse_lazy to avoid circular dependency during URL loading
PASSWORD_RESET_DONE_URL = reverse_lazy("accounts:password_reset_done")
PASSWORD_RESET_COMPLETE_URL = reverse_lazy("accounts:password_reset_complete")
PASSWORD_CHANGE_DONE_URL = reverse_lazy("accounts:password_change_done")

schema_view = get_schema_view(
    openapi.Info(
        title="FinAsis API",
        default_version="v1",
        description="FinAsis kullanıcı ve finansal API dokümantasyonu",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # ========================================================================
    # Home & Core Views
    # ========================================================================
    path("", views.accounts_home, name="accounts_home"),
    path("profile/", views.user_profile, name="user_profile"),
    path("settings/", views.user_settings, name="user_settings"),
    path("invoices/", views.user_invoices, name="user_invoices"),
    # ========================================================================
    # Company Management
    # ========================================================================
    path("company/", views.company_detail, name="company_detail"),
    path("company/edit/", views.company_edit, name="company_edit"),
    # ========================================================================
    # Authentication & Registration
    # ========================================================================
    path("register/", views.register, name="register"),
    path(
        "login/",
        rate_limit_login(
            views_auth.OTPLoginView.as_view(template_name="registration/login.html")
        ),
        name="login",
    ),
    path("logout/", views.custom_logout, name="logout"),
    # ========================================================================
    # Multi-Factor Authentication (MFA/OTP)
    # ========================================================================
    path("otp/setup/", views_mfa.otp_setup, name="otp_setup"),
    path("otp/verify/", views_mfa.otp_verify, name="otp_verify"),
    path("otp/disable/", views_mfa.otp_disable, name="otp_disable"),
    # ========================================================================
    # Password Reset Flow
    # ========================================================================
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            success_url=PASSWORD_RESET_DONE_URL,
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url=PASSWORD_RESET_COMPLETE_URL,
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    # ========================================================================
    # Password Change Flow
    # ========================================================================
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/password_change_form.html",
            success_url=PASSWORD_CHANGE_DONE_URL,
        ),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done.html"
        ),
        name="password_change_done",
    ),
    # ========================================================================
    # REST API Endpoints
    # ========================================================================
    path("api/profile/", UserProfileView.as_view(), name="api_profile"),
    path("api/company/", CompanyView.as_view(), name="api_company"),
    path("api/achievements/", AchievementsView.as_view(), name="api_achievements"),
    path("api/settings/", UserSettingsView.as_view(), name="api_settings"),
    path("api/v1/panel/", panel_data_api, name="api_panel_data"),
    path("api/docs/", schema_view.with_ui("swagger", cache_timeout=0), name="api_docs"),
    path("api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="api_redoc"),
    # ========================================================================
    # Nested App Includes
    # Note: These should ideally be in root urls.py, but kept here for backward compatibility
    # ========================================================================
    path(
        "ai-assistant/",
        include(("ai_assistant.urls", "ai_assistant"), namespace="ai_assistant"),
    ),
    path("finance/", include(("finance.urls", "finance"), namespace="finance")),
    path("education/", include(("education.urls", "education"), namespace="education")),
    path(
        "blockchain/",
        include(("blockchain.urls", "blockchain"), namespace="blockchain"),
    ),
    # ========================================================================
    # Module-Specific Views
    # ========================================================================
    path("kobi/modul/", views.modul_kobi, name="modul_kobi"),
    path("egitimci/modul/", views.modul_egitimci, name="modul_egitimci"),
    path("ogrenci/modul/", views.modul_ogrenci, name="modul_ogrenci"),
    path("oyuncu/modul/", views.modul_oyuncu, name="modul_oyuncu"),
    path("muhasebe/modul/", views.modul_muhasebe, name="modul_muhasebe"),
    path("satis/modul/", views.modul_satis, name="modul_satis"),
    path("depo/modul/", views.modul_depo, name="modul_depo"),
    path("premium/ozellik/", views.premium_feature, name="premium_feature"),
    # ========================================================================
    # Legacy Redirects (for backward compatibility)
    # ========================================================================
    path(
        "user_settings/",
        RedirectView.as_view(pattern_name="accounts:user_settings", permanent=False),
    ),
    path(
        "change-subscription/",
        views.change_subscription,
        name="change_subscription_legacy",
    ),
]

# Not: 'invoices/list.html' template dosyasını 'FinAsisV1/apps/accounts/templates/invoices/list.html' olarak oluşturmalısınız.
