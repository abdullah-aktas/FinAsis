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
from .forms import UserRegistrationForm, UserUpdateForm
from .models import User
from .tkinter_settings import open_settings_window
import threading

def login_view(request):
    """Kullanıcı girişi görünümü"""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

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