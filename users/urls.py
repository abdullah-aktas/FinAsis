from django.urls import path
from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

from . import views

app_name = 'users'

urlpatterns = [
    # Kullanıcı kayıt, giriş, çıkış
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='users:login'), name='logout'),
    
    # Kullanıcı profili
    path('profile/', views.UserProfileDetailView.as_view(), name='profile'),
    path('profile/edit/', views.UserProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/account/edit/', views.UserUpdateView.as_view(), name='account_edit'),
    
    # Kontrol paneli
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Şifre sıfırlama
    path('password-reset/', 
        PasswordResetView.as_view(
            template_name='users/password_reset.html',
            email_template_name='users/password_reset_email.html',
            subject_template_name='users/password_reset_subject.txt',
            success_url='/users/password-reset/done/'
        ), 
        name='password_reset'
    ),
    path('password-reset/done/', 
        PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ), 
        name='password_reset_done'
    ),
    path('password-reset-confirm/<uidb64>/<token>/', 
        PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            success_url='/users/password-reset-complete/'
        ), 
        name='password_reset_confirm'
    ),
    path('password-reset-complete/', 
        PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ), 
        name='password_reset_complete'
    ),
] 