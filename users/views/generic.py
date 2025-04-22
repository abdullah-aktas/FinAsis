from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from .models import User, UserProfile
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, UserUpdateForm

class UserRegistrationView(CreateView):
    """Kullanıcı kayıt görünümü"""
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/registration.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Hesabınız başarıyla oluşturuldu! Şimdi giriş yapabilirsiniz.'))
        return response

def login_view(request):
    """Kullanıcı giriş görünümü"""
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'dashboard')
                messages.success(request, _('Başarıyla giriş yaptınız!'))
                return redirect(next_url)
            else:
                messages.error(request, _('Geçersiz e-posta veya şifre.'))
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})

class UserProfileDetailView(LoginRequiredMixin, DetailView):
    """Kullanıcı profil detay görünümü"""
    model = UserProfile
    template_name = 'users/profile_detail.html'
    context_object_name = 'profile'
    
    def get_object(self):
        return get_object_or_404(UserProfile, user=self.request.user)

class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Kullanıcı profil güncelleme görünümü"""
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Profiliniz başarıyla güncellendi!'))
        return response

class UserUpdateView(LoginRequiredMixin, UpdateView):
    """Kullanıcı bilgileri güncelleme görünümü"""
    model = User
    form_class = UserUpdateForm
    template_name = 'users/user_edit.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Kullanıcı bilgileriniz başarıyla güncellendi!'))
        return response

@login_required
def dashboard_view(request):
    """Kullanıcı kontrol paneli görünümü"""
    return render(request, 'users/dashboard.html') 