from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordChangeView
)
from django.urls import reverse_lazy
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from .forms import UserRegistrationForm, UserUpdateForm
from .models import User
from .tkinter_settings import open_settings_window
import threading
import json

def login_view(request):
    """Kullanıcı girişi görünümü"""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = request.POST.get('remember', 'off') == 'on'
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Kullanıcı adı ve şifre kontrolü başarılı
                
                # Hesabın kilitli olup olmadığını kontrol et
                if hasattr(user, 'account_locked_until') and user.account_locked_until:
                    if user.account_locked_until > timezone.now():
                        messages.error(
                            request, 
                            f'Hesabınız geçici olarak kilitlendi. Lütfen daha sonra tekrar deneyin.'
                        )
                        return render(request, 'accounts/login.html', {'form': form})
                
                # Başarısız giriş sayacını sıfırla
                if hasattr(user, 'failed_login_attempts'):
                    user.failed_login_attempts = 0
                    user.save(update_fields=['failed_login_attempts'])
                
                # Kullanıcı IP adresini kaydet
                if hasattr(user, 'last_login_ip'):
                    user.last_login_ip = get_client_ip(request)
                    user.save(update_fields=['last_login_ip'])
                
                # Kullanıcı için giriş işlemi
                login(request, user)
                
                # JWT token oluştur
                token_info = get_tokens_for_user(user, remember_me)
                
                # AJAX isteği ise JSON yanıtı döndür
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'redirect': request.GET.get('next', 'home'),
                        'tokens': token_info
                    })
                
                # Normal form gönderimi ise yönlendir
                next_url = request.GET.get('next', 'home')
                response = redirect(next_url)
                
                # Token'ları cookie'ye ekle (opsiyonel güvenlik için)
                return response
            else:
                # Kimlik doğrulama başarısız, hata mesajı göster
                messages.error(request, 'Kullanıcı adı veya şifre hatalı.')
    else:
        form = AuthenticationForm()
        
    context = {
        'form': form,
        'session_expired': request.GET.get('session_expired', False)
    }
    
    return render(request, 'accounts/login.html', context)

def get_tokens_for_user(user, remember_me=False):
    """
    Kullanıcı için JWT token oluşturur
    """
    refresh = RefreshToken.for_user(user)
    
    # Remember me seçeneği için refresh token süresini uzat
    if remember_me:
        refresh.set_exp(
            lifetime=getattr(settings, 'SIMPLE_JWT', {}).get(
                'REMEMBER_ME_LIFETIME', 
                timezone.timedelta(days=7)
            )
        )
    
    # Admin kullanıcıları için access token süresini uzat
    if user.is_superuser or user.is_staff:
        access_token_lifetime = getattr(settings, 'SIMPLE_JWT', {}).get(
            'ADMIN_ACCESS_TOKEN_LIFETIME', 
            timezone.timedelta(hours=2)
        )
        refresh.access_token.set_exp(lifetime=access_token_lifetime)
    
    # Token bilgilerini döndür
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def get_client_ip(request):
    """
    İstemci IP adresini döndürür
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def register_view(request):
    """Kullanıcı kaydı görünümü"""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Hesabınız başarıyla oluşturuldu.')
            return redirect('home')
    else:
        form = UserRegistrationForm()
        
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def logout_view(request):
    """Kullanıcı çıkışı görünümü"""
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız.')
    return redirect('accounts:login')

@login_required
def profile_view(request):
    """Kullanıcı profili görünümü"""
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profiliniz başarıyla güncellendi.')
            return redirect('accounts:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def settings_view(request):
    """Kullanıcı ayarları görünümü"""
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ayarlarınız başarıyla güncellendi.')
            return redirect('accounts:settings')
    else:
        form = UserUpdateForm(instance=request.user)
    
    # Tkinter penceresini ayrı bir thread'de aç
    thread = threading.Thread(target=open_settings_window, args=(request.user,))
    thread.daemon = True
    thread.start()
    
    context = {
        'form': form,
        'user': request.user
    }
    return render(request, 'accounts/settings.html', context)

class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    from_email = settings.DEFAULT_FROM_EMAIL

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'

class CustomPasswordChangeView(PasswordChangeView):
    """Özel şifre değiştirme görünümü"""
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:settings')
    
    def form_valid(self, form):
        messages.success(self.request, 'Şifreniz başarıyla değiştirildi.')
        return super().form_valid(form) 