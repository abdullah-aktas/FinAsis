from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserProfile, UserPreferences, UserActivity, UserNotification, UserSession

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser', 'date_joined',
            'last_login', 'email_verified'
        ]
        read_only_fields = [
            'id', 'is_staff', 'is_superuser', 'date_joined',
            'last_login', 'email_verified'
        ]

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'phone', 'address', 'city', 'country',
            'postal_code', 'birth_date', 'gender', 'avatar',
            'bio', 'website', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = [
            'id', 'user', 'language', 'timezone', 'theme',
            'notifications_enabled', 'email_notifications',
            'push_notifications', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'action', 'details', 'ip_address',
            'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']

class UserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotification
        fields = [
            'id', 'user', 'title', 'message', 'type',
            'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']

class UserSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = [
            'id', 'user', 'session_key', 'ip_address',
            'user_agent', 'last_activity', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']

class UserLoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user'] = UserSerializer(self.user).data
        return data

class UserPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu e-posta adresi ile kayıtlı kullanıcı bulunamadı.")
        return value

class UserPasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Eski şifre yanlış.")
        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value

class UserEmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu e-posta adresi ile kayıtlı kullanıcı bulunamadı.")
        return value

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'phone', 'address', 'city', 'country',
            'postal_code', 'birth_date', 'gender',
            'avatar', 'bio', 'website'
        ]

    def validate_phone(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("Telefon numarası sadece rakamlardan oluşmalıdır.")
        return value

    def validate_postal_code(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("Posta kodu sadece rakamlardan oluşmalıdır.")
        return value

class UserPreferencesUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = [
            'language', 'timezone', 'theme',
            'notifications_enabled', 'email_notifications',
            'push_notifications'
        ]

    def validate_language(self, value):
        if value not in ['tr', 'en']:
            raise serializers.ValidationError("Desteklenmeyen dil seçeneği.")
        return value

    def validate_timezone(self, value):
        if value not in ['Europe/Istanbul', 'UTC']:
            raise serializers.ValidationError("Desteklenmeyen saat dilimi.")
        return value

    def validate_theme(self, value):
        if value not in ['light', 'dark', 'system']:
            raise serializers.ValidationError("Desteklenmeyen tema seçeneği.")
        return value 