from django.urls import path, include
from django.views.generic import RedirectView
from . import views
from .api import UserProfileView, CompanyView, AchievementsView, UserSettingsView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

app_name = 'accounts'

schema_view = get_schema_view(
    openapi.Info(
        title="FinAsis API",
        default_version='v1',
        description="FinAsis kullanıcı ve finansal API dokümantasyonu",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', views.accounts_home, name='accounts_home'),
    # Buraya views ekleyebilirsiniz
    path('invoices/', views.user_invoices, name='user_invoices'),
    path('profile/', views.user_profile, name='user_profile'),
    path('company/', views.company_detail, name='company_detail'),
    path('company/edit/', views.company_edit, name='company_edit'),
    path('settings/', views.user_settings, name='user_settings'),
    # Legacy path redirect for backward compatibility
    path('user_settings/', RedirectView.as_view(pattern_name='user_settings', permanent=False)),
    path('register/', views.register, name='register'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    # API
    path('api/profile/', UserProfileView.as_view(), name='api_profile'),
    path('api/company/', CompanyView.as_view(), name='api_company'),
    path('api/achievements/', AchievementsView.as_view(), name='api_achievements'),
    path('api/settings/', UserSettingsView.as_view(), name='api_settings'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='api_docs'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='api_redoc'),
    path('ai-assistant/', include('src.apps.ai_assistant.urls')),
    path('finance/', include('src.apps.finance.urls')),
    path('education/', include('src.apps.education.urls')),
    path('blockchain/', include('src.apps.blockchain.urls')),
    path('kobi/modul/', views.modul_kobi, name='modul_kobi'),
    path('egitimci/modul/', views.modul_egitimci, name='modul_egitimci'),
    path('ogrenci/modul/', views.modul_ogrenci, name='modul_ogrenci'),
    path('oyuncu/modul/', views.modul_oyuncu, name='modul_oyuncu'),
    path('premium/ozellik/', views.premium_feature, name='premium_feature'),
]

# Not: 'invoices/list.html' template dosyasını 'FinAsisV1/apps/accounts/templates/invoices/list.html' olarak oluşturmalısınız.