# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.core.cache import cache
from django.utils import timezone
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from ..forms import UserRegistrationForm, TwoFactorForm
from ..models import User
from ..utils.helpers import get_client_ip
from ..mixins.auth import LoginRequiredMixin

class LoginView(View):
    """Gelişmiş kullanıcı girişi görünümü"""
    template_name = 'accounts/auth/login.html'
    
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
    template_name = 'accounts/auth/two_factor.html'
    
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
        
    return render(request, 'accounts/auth/register.html', {'form': form})

@login_required
def logout_view(request):
    """Kullanıcı çıkışı görünümü"""
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız.')
    return redirect('accounts:login')

def get_tokens_for_user(user, remember_me=False):
    """Kullanıcı için JWT token oluşturur"""
    refresh = RefreshToken.for_user(user)
    
    if remember_me:
        refresh.set_exp(
            lifetime=getattr(settings, 'SIMPLE_JWT', {}).get(
                'REMEMBER_ME_LIFETIME', 
                timezone.timedelta(days=7)
            )
        )
    
    if user.is_superuser or user.is_staff:
        access_token_lifetime = getattr(settings, 'SIMPLE_JWT', {}).get(
            'ADMIN_ACCESS_TOKEN_LIFETIME', 
            timezone.timedelta(hours=2)
        )
        refresh.access_token.set_exp(lifetime=access_token_lifetime)
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    } 