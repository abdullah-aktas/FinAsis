from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

# API Router
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'profiles', views.UserProfileViewSet, basename='profile')
router.register(r'preferences', views.UserPreferencesViewSet, basename='preferences')
router.register(r'activities', views.UserActivityViewSet, basename='activity')
router.register(r'notifications', views.UserNotificationViewSet, basename='notification')
router.register(r'sessions', views.UserSessionViewSet, basename='session')

# URL Patterns
urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    path('api/login/', views.UserLoginView.as_view(), name='api-login'),
    path('api/logout/', views.UserLogoutView.as_view(), name='api-logout'),
    path('api/password-reset/', views.UserPasswordResetView.as_view(), name='api-password-reset'),
    path('api/password-change/', views.UserPasswordChangeView.as_view(), name='api-password-change'),
    path('api/email-verify/<str:uidb64>/<str:token>/', views.UserEmailVerificationView.as_view(), name='api-email-verify'),
    path('api/profile/update/', views.UserProfileUpdateView.as_view(), name='api-profile-update'),
    path('api/preferences/update/', views.UserPreferencesUpdateView.as_view(), name='api-preferences-update'),
    path('api/activities/', views.UserActivityListView.as_view(), name='api-activity-list'),
    path('api/notifications/', views.UserNotificationListView.as_view(), name='api-notification-list'),
    path('api/sessions/', views.UserSessionListView.as_view(), name='api-session-list'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('password-change/', views.PasswordChangeView.as_view(), name='password-change'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset.html',
        email_template_name='users/password_reset_email.html',
        subject_template_name='users/password_reset_subject.txt',
        success_url=reverse_lazy('users:password_reset_done')
    ), name='password-reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html',
        success_url=reverse_lazy('users:password_reset_complete')
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Profile URLs
    path('profile/<str:username>/', views.UserProfileView.as_view(), name='profile'),
    path('profile/edit/', views.UserProfileUpdateView.as_view(), name='profile-edit'),
    path('settings/', views.UserSettingsView.as_view(), name='settings'),
    
    # Security URLs
    path('two-factor/setup/', views.TwoFactorSetupView.as_view(), name='two-factor-setup'),
    path('two-factor/verify/', views.TwoFactorVerifyView.as_view(), name='two-factor-verify'),
    
    # Activity URLs
    path('activity/', views.UserActivityView.as_view(), name='activity'),
    
    # User Management URLs
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<str:username>/', views.UserDetailView.as_view(), name='user-detail'),
] 