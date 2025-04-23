from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import get_object_or_404, render, redirect
from rest_framework import viewsets, status, permissions
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
from .forms import (
    UserRegistrationForm, UserProfileForm, UserPreferencesForm,
    TwoFactorSetupForm, TwoFactorVerifyForm, PasswordChangeForm,
    EmailVerificationForm, PasswordResetForm, PasswordResetConfirmForm,
    UserSearchForm, UserSettingsForm
)
from .models import User, UserProfile, UserPreferences, UserActivity, UserNotification, UserSession, TwoFactorAuth, UserSettings
from .serializers import (
    UserSerializer, UserProfileSerializer, UserPreferencesSerializer,
    UserActivitySerializer, UserNotificationSerializer, UserSessionSerializer,
    UserLoginSerializer, UserPasswordResetSerializer, UserPasswordChangeSerializer,
    UserEmailVerificationSerializer, UserProfileUpdateSerializer, UserPreferencesUpdateSerializer
)
from .decorators import two_factor_required
from .tasks import send_verification_email, send_password_reset_email
from .utils import log_user_activity

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        if self.action in ['create', 'retrieve', 'update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=self.request.user)

class UserPreferencesViewSet(viewsets.ModelViewSet):
    queryset = UserPreferences.objects.all()
    serializer_class = UserPreferencesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserPreferences.objects.all()
        return UserPreferences.objects.filter(user=self.request.user)

class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserActivity.objects.all()
        return UserActivity.objects.filter(user=self.request.user)

class UserNotificationViewSet(viewsets.ModelViewSet):
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
    queryset = UserSession.objects.all()
    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserSession.objects.all()
        return UserSession.objects.filter(user=self.request.user)

class UserLoginView(TokenObtainPairView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(username=request.data.get('username'))
            UserActivity.objects.create(
                user=user,
                action='login',
                details='Kullanıcı girişi yapıldı'
            )
        return response

class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            UserActivity.objects.create(
                user=request.user,
                action='logout',
                details='Kullanıcı çıkışı yapıldı'
            )
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UserPasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserPasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = get_object_or_404(User, email=email)
            
            # Token oluştur
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # E-posta gönder
            reset_url = f"{settings.FRONTEND_URL}/password-reset/{uid}/{token}/"
            send_mail(
                'Şifre Sıfırlama',
                f'Şifrenizi sıfırlamak için bu linke tıklayın: {reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            return Response({'detail': 'Şifre sıfırlama e-postası gönderildi.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPasswordChangeView(APIView):
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
            return Response({'detail': 'Şifre başarıyla değiştirildi.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserEmailVerificationView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.email_verified = True
            user.save()
            return Response({'detail': 'E-posta adresi doğrulandı.'})
        return Response(
            {'detail': 'Geçersiz doğrulama linki.'},
            status=status.HTTP_400_BAD_REQUEST
        )

class UserProfileUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        serializer = UserProfileUpdateSerializer(data=request.data)
        if serializer.is_valid():
            profile = request.user.profile
            for key, value in serializer.validated_data.items():
                setattr(profile, key, value)
            profile.save()
            return Response(UserProfileSerializer(profile).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPreferencesUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        serializer = UserPreferencesUpdateSerializer(data=request.data)
        if serializer.is_valid():
            preferences = request.user.preferences
            for key, value in serializer.validated_data.items():
                setattr(preferences, key, value)
            preferences.save()
            return Response(UserPreferencesSerializer(preferences).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserActivityListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        activities = UserActivity.objects.filter(user=request.user).order_by('-created_at')
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)

class UserNotificationListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        notifications = UserNotification.objects.filter(user=request.user).order_by('-created_at')
        serializer = UserNotificationSerializer(notifications, many=True)
        return Response(serializer.data)

class UserSessionListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        sessions = UserSession.objects.filter(user=request.user).order_by('-last_activity')
        serializer = UserSessionSerializer(sessions, many=True)
        return Response(serializer.data)

class UserRegistrationView(SuccessMessageMixin, CreateView):
    """Kullanıcı kayıt görünümü."""
    
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    success_message = _('Kayıt başarılı! Lütfen e-posta adresinizi doğrulayın.')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        
        # Doğrulama e-postası gönder
        send_verification_email(user)
        
        # Aktivite logla
        log_user_activity(user, 'register', self.request)
        
        return response

class UserProfileView(LoginRequiredMixin, DetailView):
    """Kullanıcı profil görünümü."""
    
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        username = self.kwargs.get('username')
        return get_object_or_404(User, username=username)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_owner'] = self.request.user == self.object
        return context

class UserProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Kullanıcı profil güncelleme görünümü."""
    
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')
    success_message = _('Profil başarıyla güncellendi.')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        log_user_activity(self.object, 'profile_update', self.request)
        return response

class UserSettingsView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Kullanıcı ayarları görünümü."""
    
    model = UserSettings
    form_class = UserSettingsForm
    template_name = 'users/settings.html'
    success_url = reverse_lazy('users:settings')
    success_message = _('Ayarlar başarıyla güncellendi.')
    
    def get_object(self):
        return self.request.user.settings
    
    def form_valid(self, form):
        response = super().form_valid(form)
        log_user_activity(self.request.user, 'settings_update', self.request)
        return response

class PasswordChangeView(LoginRequiredMixin, SuccessMessageMixin, View):
    """Şifre değiştirme görünümü."""
    
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('users:profile')
    success_message = _('Şifreniz başarıyla değiştirildi.')
    
    def get(self, request):
        form = CustomPasswordChangeForm(request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            log_user_activity(user, 'password_change', request)
            messages.success(request, self.success_message)
            return redirect(self.success_url)
        return render(request, self.template_name, {'form': form})

class TwoFactorSetupView(LoginRequiredMixin, View):
    """İki faktörlü doğrulama kurulum görünümü."""
    
    template_name = 'users/two_factor_setup.html'
    
    def get(self, request):
        form = TwoFactorSetupForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = TwoFactorSetupForm(request.POST)
        if form.is_valid():
            user = request.user
            user.two_factor_enabled = True
            user.save()
            log_user_activity(user, 'two_factor_enabled', request)
            messages.success(request, _('İki faktörlü doğrulama başarıyla etkinleştirildi.'))
            return redirect('users:profile')
        return render(request, self.template_name, {'form': form})

class UserActivityView(LoginRequiredMixin, ListView):
    """Kullanıcı aktivite görünümü."""
    
    model = UserActivity
    template_name = 'users/activity.html'
    context_object_name = 'activities'
    paginate_by = 20
    
    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)

class UserListView(LoginRequiredMixin, ListView):
    """Kullanıcı listesi görünümü"""
    model = User
    template_name = 'users/user_search.html'
    context_object_name = 'users'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = User.objects.all()
        form = UserSearchForm(self.request.GET)
        
        if form.is_valid():
            query = form.cleaned_data.get('query')
            role = form.cleaned_data.get('role')
            is_active = form.cleaned_data.get('is_active')
            
            if query:
                queryset = queryset.filter(
                    Q(username__icontains=query) |
                    Q(email__icontains=query)
                )
            if role:
                queryset = queryset.filter(role=role)
            if is_active is not None:
                queryset = queryset.filter(is_active=is_active)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UserSearchForm(self.request.GET)
        return context

class UserDetailView(LoginRequiredMixin, DetailView):
    """Kullanıcı detay görünümü"""
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user_detail'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activities'] = UserActivity.objects.filter(user=self.object).order_by('-created_at')[:10]
        return context

@login_required
def user_activity(request):
    """Kullanıcı aktivite görünümü"""
    activities = UserActivity.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'users/user_activity.html', {'activities': activities}) 