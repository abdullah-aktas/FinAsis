# -*- coding: utf-8 -*-
"""
Users Modülü - View'lar
---------------------
Bu dosya, Users modülünün view'larını içerir.
"""

from django.contrib.auth import login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import get_object_or_404, render, redirect
from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.contrib.messages.views import SuccessMessageMixin
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views import View
from django.db.models import Q
from .forms import (
    UserRegistrationForm, UserProfileForm, UserPreferencesForm,
    TwoFactorSetupForm, TwoFactorVerifyForm, EmailVerificationForm,
    UserSearchForm, UserSettingsForm, PasswordChangeForm,
    PasswordResetForm, PasswordResetConfirmForm
)
from .models import User, UserProfile, UserPreferences, UserActivity, UserNotification, UserSession, TwoFactorAuth, UserSettings, UserPermission
from .serializers import (
    UserSerializer, UserProfileSerializer, UserPreferencesSerializer,
    UserActivitySerializer, UserNotificationSerializer, UserSessionSerializer,
    UserLoginSerializer, UserPasswordResetSerializer, UserPasswordChangeSerializer,
    UserEmailVerificationSerializer, UserProfileUpdateSerializer, UserPreferencesUpdateSerializer,
    UserPermissionSerializer, TwoFactorAuthSerializer, UserSettingsSerializer
)
from .decorators import two_factor_required
from .tasks import send_verification_email, send_password_reset_email
from .utils import log_user_activity
from .permissions import IsOwnerOrAdmin, IsAdminUser

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class UserProfileViewSet(viewsets.ModelViewSet):
    """Kullanıcı Profili ViewSet"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def update_profile(self, request, pk=None):
        profile = self.get_object()
        serializer = UserProfileUpdateSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPreferencesViewSet(viewsets.ModelViewSet):
    """Kullanıcı Tercihleri ViewSet"""
    queryset = UserPreferences.objects.all()
    serializer_class = UserPreferencesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserPreferences.objects.all()
        return UserPreferences.objects.filter(user=self.request.user)

class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """Kullanıcı Aktivite ViewSet"""
    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserActivity.objects.all()
        return UserActivity.objects.filter(user=self.request.user)

class UserNotificationViewSet(viewsets.ModelViewSet):
    """Kullanıcı Bildirim ViewSet"""
    queryset = UserNotification.objects.all()
    serializer_class = UserNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserNotification.objects.all()
        return UserNotification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})

class UserSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """Kullanıcı Oturum ViewSet"""
    queryset = UserSession.objects.all()
    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserSession.objects.all()
        return UserSession.objects.filter(user=self.request.user)

class UserLoginView(TokenObtainPairView):
    """Kullanıcı Giriş View"""
    serializer_class = UserLoginSerializer

class UserLogoutView(APIView):
    """Kullanıcı Çıkış View"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Başarıyla çıkış yapıldı.'})
        except Exception:
            return Response({'detail': 'Geçersiz token.'}, status=status.HTTP_400_BAD_REQUEST)

class UserRegistrationView(generics.CreateAPIView):
    """Kullanıcı Kayıt View"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        send_verification_email.delay(user.id)

class UserPasswordResetView(APIView):
    """Şifre Sıfırlama View"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserPasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = get_object_or_404(User, email=email)
            send_password_reset_email.delay(user.id)
            return Response({'detail': 'Şifre sıfırlama e-postası gönderildi.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPasswordChangeView(APIView):
    """Şifre Değiştirme View"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = UserPasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': 'Yanlış şifre.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)
            return Response({'detail': 'Şifre başarıyla değiştirildi.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(LoginRequiredMixin, DetailView):
    """Kullanıcı Profili View"""
    model = UserProfile
    template_name = 'users/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return self.request.user.profile

class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Kullanıcı Profili Güncelleme View"""
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'users/profile_update.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user.profile

class UserSettingsView(LoginRequiredMixin, UpdateView):
    """Kullanıcı Ayarları View"""
    model = UserSettings
    form_class = UserSettingsForm
    template_name = 'users/settings.html'
    success_url = reverse_lazy('users:settings')

    def get_object(self):
        return self.request.user.settings

class TwoFactorSetupView(LoginRequiredMixin, View):
    """İki Faktörlü Doğrulama Kurulum View"""
    template_name = 'users/two_factor_setup.html'

    def get(self, request):
        form = TwoFactorSetupForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = TwoFactorSetupForm(request.POST)
        if form.is_valid():
            two_factor = form.save(commit=False)
            two_factor.user = request.user
            two_factor.save()
            messages.success(request, _('İki faktörlü doğrulama başarıyla etkinleştirildi.'))
            return redirect('users:profile')
        return render(request, self.template_name, {'form': form})

class UserActivityView(LoginRequiredMixin, ListView):
    """Kullanıcı Aktivite View"""
    model = UserActivity
    template_name = 'users/activity.html'
    context_object_name = 'activities'
    paginate_by = 20

    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user).order_by('-created_at')

class UserListView(LoginRequiredMixin, ListView):
    """Kullanıcı Listesi View"""
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        queryset = User.objects.all()
        form = UserSearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            if query:
                queryset = queryset.filter(
                    Q(username__icontains=query) |
                    Q(email__icontains=query) |
                    Q(first_name__icontains=query) |
                    Q(last_name__icontains=query)
                )
        return queryset

class UserDetailView(LoginRequiredMixin, DetailView):
    """Kullanıcı Detay View"""
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user_detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activities'] = UserActivity.objects.filter(
            user=self.object
        ).order_by('-created_at')[:10]
        return context

@login_required
def user_activity(request):
    """Kullanıcı aktivite görünümü"""
    activities = UserActivity.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'users/user_activity.html', {'activities': activities})

class UserPermissionsView(generics.RetrieveAPIView):
    """Kullanıcı İzinleri View"""
    queryset = UserPermission.objects.all()
    serializer_class = UserPermissionSerializer

class CheckPermissionView(generics.RetrieveAPIView):
    """İzin Kontrol View"""
    queryset = UserPermission.objects.all()
    serializer_class = UserPermissionSerializer 