# -*- coding: utf-8 -*-
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
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework_simplejwt.tokens import RefreshToken
from ..forms import UserRegistrationForm, UserUpdateForm, TwoFactorForm
from ..models import User
# from ..tkinter_settings import open_settings_window
import threading
import json
import pyotp
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views import View

class LoginView(View):
    """Gelişmiş kullanıcı girişi görünümü"""
    template_name = 'accounts/login.html'
    
    @method_decorator(never_cache)
    @method_decorator(csrf_protect)
    @method_decorator(sensitive_post_parameters())
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        form = AuthenticationForm()
        context = {
            'form': form,
            'session_expired': request.GET.get('session_expired', False)
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = request.POST.get('remember', 'off') == 'on'
            
            # Brute force koruması
            cache_key = f'login_attempts_{username}'
            attempts = cache.get(cache_key, 0)
            if attempts >= 5:
                messages.error(request, 'Çok fazla başarısız deneme. Lütfen 15 dakika sonra tekrar deneyin.')
                return render(request, self.template_name, {'form': form})
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Hesap kilidi kontrolü
                if user.account_locked_until and user.account_locked_until > timezone.now():
                    messages.error(request, f'Hesabınız geçici olarak kilitlendi. Lütfen daha sonra tekrar deneyin.')
                    return render(request, self.template_name, {'form': form})
                
                # İki faktörlü kimlik doğrulama kontrolü
                if user.two_factor_enabled:
                    request.session['pending_user_id'] = user.id
                    return redirect('accounts:two_factor')
                
                # Başarılı giriş işlemleri
                self._handle_successful_login(request, user, remember_me)
                cache.delete(cache_key)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'redirect': request.GET.get('next', 'home'),
                        'tokens': get_tokens_for_user(user, remember_me)
                    })
                
                return redirect(request.GET.get('next', 'home'))
            else:
                # Başarısız giriş işlemleri
                cache.incr(cache_key, 1)
                cache.expire(cache_key, 900)  # 15 dakika
                messages.error(request, 'Kullanıcı adı veya şifre hatalı.')
        
        return render(request, self.template_name, {'form': form})
    
    def _handle_successful_login(self, request, user, remember_me):
        """Başarılı giriş işlemlerini yönetir"""
        user.failed_login_attempts = 0
        user.last_login_ip = get_client_ip(request)
        user.save(update_fields=['failed_login_attempts', 'last_login_ip'])
        login(request, user)
        
        # Şifre süresi kontrolü
        if user.is_password_expired():
            messages.warning(request, 'Şifrenizin süresi dolmuş. Lütfen şifrenizi değiştirin.')
            return redirect('accounts:password_change')

class TwoFactorView(View):
    """İki faktörlü kimlik doğrulama görünümü"""
    template_name = 'accounts/two_factor.html'
    
    def get(self, request):
        if 'pending_user_id' not in request.session:
            return redirect('accounts:login')
        
        form = TwoFactorForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        if 'pending_user_id' not in request.session:
            return redirect('accounts:login')
        
        form = TwoFactorForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=request.session['pending_user_id'])
            code = form.cleaned_data['code']
            
            if user.verify_two_factor_code(code):
                del request.session['pending_user_id']
                login(request, user)
                messages.success(request, 'Başarıyla giriş yaptınız.')
                return redirect('home')
            else:
                messages.error(request, 'Geçersiz doğrulama kodu.')
        
        return render(request, self.template_name, {'form': form})

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
    """Gelişmiş şifre değiştirme görünümü"""
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:settings')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Şifreniz başarıyla değiştirildi.')
        
        # Şifre değişikliği sonrası oturumu yenile
        login(self.request, self.request.user)
        
        return response
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs 