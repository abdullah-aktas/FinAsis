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
```

### Profile
```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True)
    website = models.URLField(blank=True)
```

## View'lar

### Authentication Views
- `LoginView`: Kullanıcı girişi
- `LogoutView`: Kullanıcı çıkışı
- `PasswordResetView`: Şifre sıfırlama
- `PasswordResetConfirmView`: Şifre sıfırlama onayı
- `PasswordChangeView`: Şifre değiştirme

### User Views
- `UserCreateView`: Kullanıcı oluşturma
- `UserUpdateView`: Kullanıcı güncelleme
- `UserDeleteView`: Kullanıcı silme
- `ProfileView`: Profil görüntüleme
- `ProfileUpdateView`: Profil güncelleme

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
        fields = ['bio', 'location', 'birth_date', 'website']
```

## Kullanım Örnekleri

### Kullanıcı Oluşturma
```python
form = UserCreationForm(request.POST)
if form.is_valid():
    user = form.save()
    Profile.objects.create(user=user)
    messages.success(request, _('Kullanıcı başarıyla oluşturuldu.'))
```

### Profil Güncelleme
```python
form = ProfileForm(request.POST, instance=request.user.profile)
if form.is_valid():
    form.save()
    messages.success(request, _('Profil başarıyla güncellendi.'))
```

### Şifre Değiştirme
```python
form = PasswordChangeForm(request.user, request.POST)
if form.is_valid():
    user = form.save()
    update_session_auth_hash(request, user)
    messages.success(request, _('Şifreniz başarıyla değiştirildi.'))
```

## İzinler ve Güvenlik

- Kullanıcılar sadece kendi profillerini düzenleyebilir
- Yöneticiler tüm kullanıcıları yönetebilir
- Şifreler güvenli bir şekilde hashlenir
- Oturumlar güvenli bir şekilde yönetilir

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
    messages.error(request, str(e))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
```

## Önbellekleme

Performans için önemli veriler önbelleğe alınır:
```python
cache_key = f'user_profile_{user.id}'
profile = cache.get(cache_key)
if not profile:
    profile = Profile.objects.get(user=user)
    cache.set(cache_key, profile, 3600)  # 1 saat
``` 