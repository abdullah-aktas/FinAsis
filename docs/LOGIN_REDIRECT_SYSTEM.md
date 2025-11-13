# FinAsis - Yönlendirme Sistemi Dokümantasyonu

## Kullanıcı Giriş Sonrası Yönlendirme

Proje artık kullanıcıların giriş yaptıktan sonra direkt kendi kullandıkları panele yönlendirilmesini sağlıyor.

### Uygulanan Değişiklikler

#### 1. Yönlendirme Modülü (`accounts/utils_redirect.py`)

Yeni oluşturulan bu modül, kullanıcı tipine göre otomatik yönlendirme sağlar:

```python
def get_user_dashboard_url(user):
    """Kullanıcının tipine göre dashboard URL'ini döndürür"""

def get_redirect_after_login(request, user):
    """Giriş sonrası güvenli yönlendirme URL'ini belirler"""
```

**Desteklenen Kullanıcı Tipleri:**

- **KOBİ/SME/Business** → `/accounts/kobi/modul/`
- **Mali Müşavir/Muhasebeci** → `/accounts/profile/`
- **Eğitimci/Teacher** → `/accounts/egitimci/modul/`
- **Öğrenci/Student** → `/accounts/ogrenci/modul/`
- **Yatırımcı/Investor** → `/accounts/profile/`
- **Oyuncu/Gamer** → `/accounts/oyuncu/modul/`

#### 2. Güncellenen Login View (`accounts/views_auth.py`)

`OTPLoginView` sınıfı güncellenerek:

- Kullanıcı tipine göre dinamik yönlendirme eklendi
- MFA (Multi-Factor Authentication) sonrası da doğru yönlendirme sağlandı
- Güvenlik logları iyileştirildi

#### 3. Güncellenen MFA View (`accounts/views_mfa.py`)

`_get_safe_redirect()` fonksiyonu güncellenerek:

- MFA doğrulaması sonrası kullanıcı tipine göre yönlendirme
- Session ve GET parametrelerinden güvenli URL çıkarma
- Fallback mekanizması ile her durumda çalışma garantisi

### Yönlendirme Öncelik Sırası

1. **`next` parametresi** (GET/POST) - Güvenlik kontrolü ile
2. **Session'da kayıtlı redirect** - `post_login_redirect` veya `post_otp_redirect`
3. **Kullanıcı tipi bazlı dashboard** - `user.user_type.code`'a göre
4. **Role bazlı yönlendirme** - `user.role`'e göre (fallback)
5. **Şirket bazlı** - Eğer şirket varsa muhasebe dashboard
6. **Varsayılan** - Profil sayfası

### Güvenlik Özellikleri

✅ URL injection koruması - Sadece internal URL'lere izin
✅ Host validation - `url_has_allowed_host_and_scheme` kontrolü
✅ Audit logging - Tüm giriş ve yönlendirme işlemleri loglanıyor
✅ Session temizliği - Kullanılan redirect URL'leri session'dan temizleniyor

### Kullanım Örnekleri

#### Örnek 1: KOBİ Kullanıcısı

```python
user.user_type.code = 'kobi'
# Giriş sonrası → /accounts/kobi/modul/
```

#### Örnek 2: Öğretmen

```python
user.user_type.code = 'egitimci'
# Giriş sonrası → /accounts/egitimci/modul/
```

#### Örnek 3: Next Parametresi ile

```
/accounts/login/?next=/finance/dashboard/
# Giriş sonrası → /finance/dashboard/ (güvenli ise)
```

### Şablonlar ve UI

#### Base Template (`templates/base.html`)

- Modern, responsive tasarım
- Bootstrap 5.3 entegrasyonu
- Header ve footer component'leri
- Mesaj sistemi desteği

#### Header Component (`templates/components/header.html`)

- Kullanıcı durumuna göre dinamik menü
- Bildirim sistemi hazır
- Dil değiştirme özelliği
- Responsive mobile menü

#### Footer Component (`templates/components/footer.html`)

- Kapsamlı link yapısı
- Sosyal medya entegrasyonu
- SEO dostu yapı
- Back-to-top butonu

### Test Senaryoları

1. **Normal Giriş**

   - User type: kobi → KOBİ modülüne gider
   - User type: egitimci → Eğitimci modülüne gider

2. **MFA ile Giriş**

   - OTP doğrulama sonrası doğru dashboard'a yönlendirilir

3. **Next Parametresi ile**

   - Güvenli URL ise o sayfaya gider
   - Değilse kullanıcı tipine göre dashboard

4. **Session Redirect**
   - Session'da kayıtlı URL varsa oraya gider

### Yapılandırma

`config/settings/base.py` içinde:

```python
LOGIN_REDIRECT_URL = 'accounts:user_profile'  # Fallback
LOGOUT_REDIRECT_URL = 'accounts:login'
LOGIN_URL = 'accounts:login'
```

### İleriki Geliştirmeler İçin Öneriler

1. **Dashboard Tercihleri**: Kullanıcıların varsayılan dashboard'larını seçebilmeleri
2. **Son Görüntülenen Sayfa**: Kullanıcının son ziyaret ettiği sayfayı hatırlama
3. **Çoklu Panel Desteği**: Bir kullanıcının birden fazla role sahip olması durumu
4. **Analytics**: Kullanıcıların hangi sayfalara gittiğini takip etme

### Sorun Giderme

**Problem**: Kullanıcı giriş sonrası yanlış sayfaya gidiyor
**Çözüm**:

- `user.user_type.code` değerini kontrol edin
- Database'de `UserType` kayıtlarını inceleyin
- `utils_redirect.py` içindeki mapping'i güncelleyin

**Problem**: MFA sonrası yönlendirme çalışmıyor
**Çözüm**:

- Session'da `post_otp_redirect` kontrolü yapın
- `_get_safe_redirect()` fonksiyonunu debug edin

## Ekip İçin Notlar

- Yeni kullanıcı tipleri eklendiğinde `utils_redirect.py` güncellenmeli
- URL değişikliklerinde yönlendirme URL'lerini kontrol edin
- Test coverage artırılmalı (unit testler önerilir)

---

**Geliştirici**: GitHub Copilot  
**Tarih**: 13 Kasım 2025  
**Versiyon**: 1.0
