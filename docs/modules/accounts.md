# Accounts Modülü

## Genel Bakış
Accounts modülü, kullanıcı yönetimi, kimlik doğrulama ve yetkilendirme işlemlerini yönetir.

## Temel Özellikler

### 1. Kullanıcı Yönetimi
- Kullanıcı kaydı
- Profil yönetimi
- Şifre yönetimi
- Yetki yönetimi

### 2. Kimlik Doğrulama
- Giriş/çıkış işlemleri
- Oturum yönetimi
- Şifre sıfırlama
- E-posta doğrulama

### 3. Yetkilendirme
- Rol tabanlı erişim kontrolü
- İzin yönetimi
- Grup yönetimi

### 4. Güvenlik
- İki faktörlü doğrulama (2FA)
- Oturum güvenliği
- Şifre politikaları
- Güvenlik günlükleri

## Modeller

### User
```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True)
    last_password_change = models.DateTimeField(null=True)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=100, blank=True)
```

### Profile
```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True)
    website = models.URLField(blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='tr')
```

### UserPreferences
```python
class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme = models.CharField(max_length=20, default='light')
    notifications_enabled = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
```

## View'lar

### Authentication Views
- `LoginView`: Kullanıcı girişi
- `LogoutView`: Kullanıcı çıkışı
- `PasswordResetView`: Şifre sıfırlama
- `PasswordResetConfirmView`: Şifre sıfırlama onayı
- `PasswordChangeView`: Şifre değiştirme
- `TwoFactorSetupView`: İki faktörlü doğrulama kurulumu
- `TwoFactorVerifyView`: İki faktörlü doğrulama onayı

### User Views
- `UserCreateView`: Kullanıcı oluşturma
- `UserUpdateView`: Kullanıcı güncelleme
- `UserDeleteView`: Kullanıcı silme
- `ProfileView`: Profil görüntüleme
- `ProfileUpdateView`: Profil güncelleme
- `UserPreferencesView`: Kullanıcı tercihleri
- `UserSessionView`: Oturum yönetimi

## Formlar

### UserCreationForm
```python
class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Şifre', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Şifre Tekrar', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
```

### UserChangeForm
```python
class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']
```

### ProfileForm
```python
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'birth_date', 'website', 'timezone', 'language']
```

### TwoFactorSetupForm
```python
class TwoFactorSetupForm(forms.Form):
    enable_2fa = forms.BooleanField(required=False)
    verification_code = forms.CharField(max_length=6, required=False)
```

## Kullanım Örnekleri

### Kullanıcı Oluşturma
```python
form = UserCreationForm(request.POST)
if form.is_valid():
    user = form.save()
    Profile.objects.create(user=user)
    UserPreferences.objects.create(user=user)
    messages.success(request, _('Kullanıcı başarıyla oluşturuldu.'))
```

### Profil Güncelleme
```python
form = ProfileForm(request.POST, instance=request.user.profile)
if form.is_valid():
    form.save()
    messages.success(request, _('Profil başarıyla güncellendi.'))
```

### İki Faktörlü Doğrulama
```python
form = TwoFactorSetupForm(request.POST)
if form.is_valid():
    if form.cleaned_data['enable_2fa']:
        # 2FA kurulumu
        user.two_factor_enabled = True
        user.two_factor_secret = generate_secret()
        user.save()
        messages.success(request, _('İki faktörlü doğrulama etkinleştirildi.'))
```

## İzinler ve Güvenlik

- Kullanıcılar sadece kendi profillerini düzenleyebilir
- Yöneticiler tüm kullanıcıları yönetebilir
- Şifreler güvenli bir şekilde hashlenir
- Oturumlar güvenli bir şekilde yönetilir
- İki faktörlü doğrulama zorunlu olabilir
- Şifre politikaları uygulanır
- Güvenlik günlükleri tutulur

## AJAX Desteği

Tüm view'lar AJAX isteklerini destekler:
```python
if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    return JsonResponse({
        'success': True,
        'message': _('İşlem başarılı.'),
        'data': {...}
    })
```

## Hata Yönetimi

Tüm view'lar hata durumlarını uygun şekilde yönetir:
```python
try:
    # İşlem
except Exception as e:
    return JsonResponse({
        'success': False,
        'message': str(e),
        'error_code': 'ERROR_CODE'
    })
```

## API Endpoints

### Kullanıcı İşlemleri
- `POST /api/users/`: Yeni kullanıcı oluştur
- `GET /api/users/me/`: Mevcut kullanıcı bilgilerini getir
- `PUT /api/users/me/`: Kullanıcı bilgilerini güncelle
- `POST /api/users/password-reset/`: Şifre sıfırlama isteği
- `POST /api/users/password-reset-confirm/`: Şifre sıfırlama onayı

### Profil İşlemleri
- `GET /api/profiles/me/`: Profil bilgilerini getir
- `PUT /api/profiles/me/`: Profil bilgilerini güncelle
- `GET /api/profiles/preferences/`: Kullanıcı tercihlerini getir
- `PUT /api/profiles/preferences/`: Kullanıcı tercihlerini güncelle

### Güvenlik İşlemleri
- `POST /api/security/2fa/setup/`: İki faktörlü doğrulama kurulumu
- `POST /api/security/2fa/verify/`: İki faktörlü doğrulama onayı
- `GET /api/security/sessions/`: Aktif oturumları listele
- `DELETE /api/security/sessions/{id}/`: Oturumu sonlandır 