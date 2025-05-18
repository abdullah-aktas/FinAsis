# Güvenlik ve Kimlik Doğrulama

Bu dokümantasyon, FinAsis projesinin güvenlik özelliklerini ve kimlik doğrulama mekanizmalarını detaylandırmaktadır.

## İçindekiler

1. [Genel Bakış](#genel-bakış)
2. [Kimlik Doğrulama](#kimlik-doğrulama)
3. [Yetkilendirme](#yetkilendirme)
4. [Veri Güvenliği](#veri-güvenliği)
5. [API Güvenliği](#api-güvenliği)
6. [Güvenlik Kontrolleri](#güvenlik-kontrolleri)
7. [Güvenlik En İyi Uygulamaları](#güvenlik-en-iyi-uygulamaları)

## Genel Bakış

FinAsis, aşağıdaki güvenlik özelliklerini içerir:

- JWT tabanlı kimlik doğrulama
- İki faktörlü kimlik doğrulama (2FA)
- Rol tabanlı erişim kontrolü (RBAC)
- API rate limiting
- Veri şifreleme
- Güvenlik denetimleri
- Güvenlik duvarı yapılandırması

## Kimlik Doğrulama

### JWT Kimlik Doğrulama

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

### İki Faktörlü Kimlik Doğrulama (2FA)

```python
# models.py
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, null=True, blank=True)
    backup_codes = models.JSONField(null=True, blank=True)
```

### Şifre Politikası

```python
# validators.py
class PasswordValidator:
    def validate(self, password):
        if len(password) < 8:
            raise ValidationError("Şifre en az 8 karakter olmalıdır.")
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Şifre en az bir büyük harf içermelidir.")
        if not re.search(r"[a-z]", password):
            raise ValidationError("Şifre en az bir küçük harf içermelidir.")
        if not re.search(r"\d", password):
            raise ValidationError("Şifre en az bir rakam içermelidir.")
```

## Yetkilendirme

### Rol Tabanlı Erişim Kontrolü (RBAC)

```python
# permissions.py
class RoleBasedPermission:
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        required_permission = getattr(view, 'required_permission', None)
        if not required_permission:
            return True
            
        return request.user.has_permission(required_permission)
```

### İzin Grupları

```python
# groups.py
PERMISSION_GROUPS = {
    'admin': [
        'user_management',
        'system_configuration',
        'audit_logs'
    ],
    'accountant': [
        'view_accounts',
        'create_transactions',
        'view_reports'
    ],
    'user': [
        'view_own_accounts',
        'create_own_transactions'
    ]
}
```

## Veri Güvenliği

### Veri Şifreleme

```python
# encryption.py
from cryptography.fernet import Fernet

class DataEncryption:
    def __init__(self):
        self.key = settings.ENCRYPTION_KEY
        self.cipher_suite = Fernet(self.key)
    
    def encrypt(self, data):
        return self.cipher_suite.encrypt(data.encode())
    
    def decrypt(self, encrypted_data):
        return self.cipher_suite.decrypt(encrypted_data).decode()
```

### Hassas Veri Yönetimi

```python
# sensitive_data.py
class SensitiveDataHandler:
    def mask_credit_card(self, card_number):
        return f"**** **** **** {card_number[-4:]}"
    
    def mask_tax_number(self, tax_number):
        return f"*** *** {tax_number[-3:]}"
```

## API Güvenliği

### Rate Limiting

```python
# throttling.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'premium': '5000/hour'
    }
}
```

### API Anahtarı Yönetimi

```python
# api_keys.py
class APIKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True)
```

## Güvenlik Kontrolleri

### Güvenlik Duvarı Kuralları

```nginx
# nginx.conf
# DDoS koruması
limit_req_zone $binary_remote_addr zone=one:10m rate=1r/s;
limit_req zone=one burst=10 nodelay;

# Kötü niyetli botları engelleme
if ($http_user_agent ~* (bot|crawler|spider|scan)) {
    return 403;
}

# SSL yapılandırması
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;
```

### Güvenlik Denetimleri

```python
# security_checks.py
class SecurityAudit:
    def check_password_strength(self, password):
        return self.password_validator.validate(password)
    
    def check_session_security(self, request):
        return {
            'ip_changed': self.check_ip_change(request),
            'user_agent_changed': self.check_user_agent_change(request),
            'suspicious_activity': self.check_suspicious_activity(request)
        }
```

## Güvenlik En İyi Uygulamaları

### Şifre Politikası

- Minimum 8 karakter
- En az bir büyük harf
- En az bir küçük harf
- En az bir rakam
- En az bir özel karakter
- 90 günde bir şifre değişikliği zorunluluğu

### Oturum Yönetimi

- 30 dakika hareketsizlik sonrası otomatik çıkış
- Eşzamanlı oturum sınırlaması
- IP değişikliğinde yeniden kimlik doğrulama
- Şüpheli aktivite tespitinde oturum sonlandırma

### Veri Güvenliği

- Tüm hassas veriler şifrelenir
- Yedekleme verileri şifrelenir
- Veri transferi SSL/TLS ile korunur
- Düzenli güvenlik denetimleri yapılır

### Güvenlik Güncellemeleri

- Haftalık güvenlik yamaları
- Bağımlılık güvenlik taramaları
- Güvenlik açığı bildirimi ve düzeltme süreci
- Güvenlik olaylarına müdahale planı 