from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from datetime import timedelta

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Özelleştirilmiş JWT token serializer'ı.
    
    Bu serializer, farklı kullanıcı tipleri için farklı token ömürleri ve 
    hatırla seçeneği (remember_me) sunar.
    """
    remember_me = serializers.BooleanField(required=False, default=False)
    device_type = serializers.CharField(required=False, default='web')
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Token'a kullanıcı bilgilerini ekle
        token['username'] = user.username
        token['email'] = user.email
        
        # Admin kontrolü
        is_admin = user.is_superuser or user.is_staff
        token['is_admin'] = is_admin
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Token içeriğini oluştur
        refresh = self.get_token(self.user)
        
        # Kullanıcı tipine göre token süresini ayarla
        if attrs.get('device_type') == 'mobile':
            # Mobil cihazlar için daha kısa token süresi
            access_token_lifetime = settings.SIMPLE_JWT.get('MOBILE_ACCESS_TOKEN_LIFETIME', 
                                                           timedelta(minutes=30))
        elif attrs.get('remember_me'):
            # Remember me seçeneği ile uzun süreli token
            access_token_lifetime = settings.SIMPLE_JWT.get('REMEMBER_ME_LIFETIME', 
                                                          timedelta(days=7))
        elif self.user.is_superuser or self.user.is_staff:
            # Admin kullanıcılar için daha uzun token süresi
            access_token_lifetime = settings.SIMPLE_JWT.get('ADMIN_ACCESS_TOKEN_LIFETIME', 
                                                          timedelta(hours=2))
        else:
            # Standart kullanıcılar için default süre
            access_token_lifetime = settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME', 
                                                          timedelta(minutes=60))
        
        # Token'ı uygun süre ile oluştur
        refresh.access_token.set_exp(lifetime=access_token_lifetime)
        
        # Remember me seçeneği için refresh token süresini uzat
        if attrs.get('remember_me'):
            refresh_token_lifetime = settings.SIMPLE_JWT.get('REMEMBER_ME_LIFETIME', 
                                                           timedelta(days=7))
            refresh.set_exp(lifetime=refresh_token_lifetime)
        
        # Token'ları döndür
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        
        # Ekstra bilgileri ekle
        data['user_id'] = self.user.id
        data['username'] = self.user.username
        data['is_admin'] = self.user.is_superuser or self.user.is_staff
        
        return data

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    """
    Özelleştirilmiş token yenileme serializer'ı.
    
    Bu serializer, token yenileme sırasında eski token'ı blacklist'e ekler
    ve yeni bir token üretir.
    """
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Refresh token'dan kullanıcı bilgilerini almalıyız, 
        # ancak SimpleJWT bunu doğrudan sağlamaz.
        # Token yenileme sırasında token sürelerini değiştirmek için özel bir 
        # sınıf gerekebilir.
        
        return data 