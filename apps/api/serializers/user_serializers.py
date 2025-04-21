"""
Kullanıcı serileştiricileri
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Kullanıcı serileştirici"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'is_active', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']
        
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Özelleştirilmiş token serileştirici"""
    
    def validate(self, attrs):
        """Token doğrulama ve oluşturma"""
        data = super().validate(attrs)
        
        # Token'a ek kullanıcı bilgileri ekle
        user = self.user
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
        }
        
        return data 