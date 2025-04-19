# FinAsis Geliştirici Rehberi

## İçindekiler
1. [Proje Yapısı](#1-proje-yapısı)
2. [Kurulum](#2-kurulum)
3. [Mimari](#3-mimari)
4. [Veri Modelleri](#4-veri-modelleri)
5. [API Dokümantasyonu](#5-api-dokümantasyonu)
6. [Frontend](#6-frontend)
7. [Masaüstü Uygulaması](#7-masaüstü-uygulaması)
8. [Entegrasyonlar](#8-entegrasyonlar)
9. [Test](#9-test)
10. [Dağıtım](#10-dağıtım)
11. [Sorun Giderme ve Hata Ayıklama](#11-sorun-giderme-ve-hata-ayıklama)
12. [Sürüm Yönetimi](#12-sürüm-yönetimi)

## 1. Proje Yapısı

FinAsis, Django tabanlı bir web uygulaması ve Python/Tkinter tabanlı bir masaüstü uygulamasından oluşan kapsamlı bir finansal yönetim sistemidir. Proje, aşağıdaki ana bileşenlerden oluşmaktadır:

```
finasis/
│
├── apps/                    # Django uygulamaları
│   ├── accounts/            # Kullanıcı hesapları ve yetkilendirme
│   ├── accounting/          # Muhasebe modülü
│   ├── crm/                 # Müşteri İlişkileri Modülü
│   └── virtual_company/     # Sanal şirket simülasyonu
│
├── config/                  # Django projesinin yapılandırma dosyaları
│   ├── settings/            # Ortam bazlı ayarlar (dev, prod, test)
│   ├── urls.py              # Ana URL yapılandırması
│   └── wsgi.py              # WSGI yapılandırması
│
├── core/                    # Çekirdek fonksiyonlar ve ortak özellikler
│
├── docs/                    # Dokümantasyon dosyaları
│
├── scripts/                 # Yardımcı scriptler
│
├── static/                  # Statik dosyalar (CSS, JS, resimler)
│
├── templates/               # HTML şablonları
│
├── desktop_app.py           # Masaüstü uygulaması
│
├── build_desktop.py         # Masaüstü uygulaması derleme scripti
│
└── manage.py                # Django yönetim scripti
```

## 2. Kurulum

### 2.1 Geliştirme Ortamı

Geliştirme ortamını kurmak için aşağıdaki adımları izleyin:

#### Gereksinimler
- Python 3.9 veya üzeri
- pip (Python paket yöneticisi)
- Git
- PostgreSQL (opsiyonel, varsayılan olarak SQLite kullanılmaktadır)

#### Adımlar

1. Projeyi klonlayın:
```bash
git clone https://github.com/finasis/finasis.git
cd finasis
```

2. Sanal ortam oluşturun ve etkinleştirin:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

4. Veritabanını oluşturun:
```bash
python manage.py migrate
```

5. Test verilerini yükleyin (opsiyonel):
```bash
python manage.py loaddata fixtures/sample_data.json
```

6. Yönetici kullanıcısı oluşturun:
```bash
python manage.py createsuperuser
```

7. Geliştirme sunucusunu başlatın:
```bash
python manage.py runserver
```

8. Tarayıcınızda `http://127.0.0.1:8000` adresine giderek uygulamayı görüntüleyin.

### 2.2 Ortamlar

FinAsis, farklı ortamlar için ayrı ayarlar kullanır:

- **Geliştirme**: `config/settings/dev.py` - Geliştirme için kullanılır
- **Test**: `config/settings/test.py` - Test ortamı için kullanılır
- **Üretim**: `config/settings/prod.py` - Canlı ortam için kullanılır

Ortamı belirtmek için, `DJANGO_SETTINGS_MODULE` çevre değişkenini ayarlayın:

```bash
# Windows
set DJANGO_SETTINGS_MODULE=config.settings.dev

# Linux/macOS
export DJANGO_SETTINGS_MODULE=config.settings.dev
```

### 2.3 Ortam Değişkenleri

Uygulamanın çalışması için gerekli olan çevre değişkenleri `.env` dosyasında tanımlanmıştır. Örnek bir `.env` dosyası:

```
# Django
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3
# Alternatif olarak:
# DATABASE_URL=postgres://user:password@localhost:5432/finasis

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# E-Belge entegrasyonu
EDOCUMENT_API_KEY=your-api-key
EDOCUMENT_API_URL=https://api.example.com/edocument
EDOCUMENT_SERVICE_TYPE=earchive

# Şirket Bilgileri
COMPANY_VKN=1234567890
COMPANY_NAME=FinAsis Yazılım A.Ş.
COMPANY_WEBSITE=https://finasis.com.tr
COMPANY_ADDRESS=Örnek Mahallesi, Örnek Sokak No:1
COMPANY_DISTRICT=Örnek
COMPANY_CITY=İstanbul
COMPANY_POSTAL_CODE=34000
COMPANY_COUNTRY=Türkiye
COMPANY_TAX_OFFICE=İstanbul
COMPANY_PHONE=+90 850 123 45 67
COMPANY_EMAIL=info@finasis.com.tr
```

## 3. Mimari

FinAsis, Model-View-Template (MVT) mimarisini kullanan Django web framework'ü üzerine inşa edilmiştir. Web uygulamasının ana bileşenleri şunlardır:

### 3.1 Backend (Django)

- **Models**: Veritabanı şemasını ve iş mantığını tanımlar
- **Views**: Kullanıcı isteklerini işler ve uygun yanıtları döndürür
- **Templates**: Kullanıcı arayüzünü tanımlar
- **Forms**: Kullanıcı girişi ve veri doğrulama için kullanılır
- **URLs**: URL yönlendirmelerini tanımlar

### 3.2 Frontend

- **HTML/CSS/JS**: Kullanıcı arayüzü için temel yapı
- **Bootstrap 5**: Duyarlı tasarım için CSS framework'ü
- **Font Awesome**: İkonlar için
- **jQuery**: DOM manipülasyonu ve AJAX istekleri için
- **Chart.js**: Veri görselleştirme için

### 3.3 Masaüstü Uygulaması

Masaüstü uygulaması, Python ve Tkinter kullanılarak geliştirilmiştir. Uygulama, yerel bir Django sunucusunu başlatır ve web uygulamasını bir tarayıcı arayüzünde görüntüler.

### 3.4 Veritabanı

Varsayılan olarak SQLite kullanılmaktadır, ancak üretim ortamında PostgreSQL kullanılması önerilir. Veritabanı modelleri, `apps/<app_name>/models.py` dosyalarında tanımlanmıştır.

## 4. Veri Modelleri

### 4.1 Accounts (Kullanıcı Hesapları)

Ana kullanıcı modeli, Django'nun `AbstractUser` sınıfından türetilmiştir ve ek alanlar eklenmiştir:

```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    is_virtual_company_user = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
```

### 4.2 Accounting (Muhasebe)

Muhasebe modülü, aşağıdaki ana modelleri içerir:

#### 4.2.1 ChartOfAccounts (Hesap Planı)

```python
class ChartOfAccounts(BaseModel):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=[
        ('asset', 'Varlık'),
        ('liability', 'Yükümlülük'),
        ('equity', 'Özkaynak'),
        ('income', 'Gelir'),
        ('expense', 'Gider'),
    ])
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    level = models.IntegerField(default=1)
    is_leaf = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
```

#### 4.2.2 Account (Cari Hesap)

```python
class Account(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=20, choices=[
        ('customer', 'Müşteri'),
        ('supplier', 'Tedarikçi'),
        ('employee', 'Çalışan'),
        ('other', 'Diğer'),
    ])
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    vkn_tckn = models.CharField(max_length=11, blank=True, null=True)
    tax_office = models.CharField(max_length=100, blank=True, null=True)
    e_invoice_registered = models.BooleanField(default=False)
    e_archive_registered = models.BooleanField(default=False)
```

#### 4.2.3 Invoice (Fatura)

```python
class Invoice(BaseModel):
    number = models.CharField(max_length=20, unique=True)
    date = models.DateField()
    due_date = models.DateField()
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    type = models.CharField(max_length=20, choices=[
        ('sales', 'Satış Faturası'),
        ('purchase', 'Alış Faturası'),
    ])
    total = models.DecimalField(max_digits=12, decimal_places=2)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=1.0000)
    description = models.TextField(blank=True, null=True)
    e_invoice_status = models.CharField(max_length=20, choices=[
        ('draft', 'Taslak'),
        ('pending', 'Beklemede'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
        ('canceled', 'İptal Edildi'),
    ], default='draft')
    is_e_invoice = models.BooleanField(default=False)
    is_e_archive = models.BooleanField(default=False)
    e_invoice_id = models.CharField(max_length=36, blank=True, null=True)
    e_invoice_uuid = models.CharField(max_length=36, blank=True, null=True)
    is_e_invoice_suitable = models.BooleanField(default=False)
    recipient_vkn_tckn = models.CharField(max_length=11, blank=True, null=True)
    recipient_tax_office = models.CharField(max_length=100, blank=True, null=True)
    recipient_email = models.EmailField(blank=True, null=True)
```

### 4.3 CRM (Müşteri İlişkileri Yönetimi)

CRM modülü, aşağıdaki ana modelleri içerir:

#### 4.3.1 Customer (Müşteri)

```python
class Customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    tax_number = models.CharField(max_length=20, blank=True)
    tax_office = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
```

#### 4.3.2 Opportunity (Fırsat)

```python
class Opportunity(models.Model):
    name = models.CharField(max_length=200)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='opportunities')
    value = models.DecimalField(max_digits=12, decimal_places=2)
    expected_close_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('open', 'Açık'),
        ('won', 'Kazanıldı'),
        ('lost', 'Kaybedildi'),
        ('dormant', 'Uyuyan'),
    ], default='open')
    probability = models.IntegerField(default=50)
    notes = models.TextField(blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_opportunities')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 4.3.3 Activity (Aktivite)

```python
class Activity(models.Model):
    type = models.CharField(max_length=20, choices=[
        ('call', 'Telefon'),
        ('meeting', 'Toplantı'),
        ('email', 'E-posta'),
        ('task', 'Görev'),
        ('note', 'Not'),
    ])
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='activities')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_activities')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 5. API Dokümantasyonu

FinAsis, REST API'leri için Django Rest Framework (DRF) kullanmaktadır. API dokümantasyonu için Swagger/OpenAPI kullanılmaktadır.

### 5.1 API Endpoints

API endpoints, `apps/<app_name>/api.py` ve `apps/<app_name>/urls.py` dosyalarında tanımlanmıştır. 

#### 5.1.1 Kimlik Doğrulama API'leri

```
POST /api/auth/token/ - JWT token almak için
POST /api/auth/token/refresh/ - JWT token yenilemek için
POST /api/auth/register/ - Yeni kullanıcı kaydetmek için
```

#### 5.1.2 Müşteri API'leri

```
GET /api/crm/customers/ - Müşteri listesi almak için
POST /api/crm/customers/ - Yeni müşteri eklemek için
GET /api/crm/customers/{id}/ - Belirli bir müşteriyi almak için
PUT /api/crm/customers/{id}/ - Müşteri bilgilerini güncellemek için
DELETE /api/crm/customers/{id}/ - Müşteriyi silmek için
```

#### 5.1.3 Muhasebe API'leri

```
GET /api/accounting/invoices/ - Fatura listesi almak için
POST /api/accounting/invoices/ - Yeni fatura eklemek için
GET /api/accounting/invoices/{id}/ - Belirli bir faturayı almak için
PUT /api/accounting/invoices/{id}/ - Fatura bilgilerini güncellemek için
DELETE /api/accounting/invoices/{id}/ - Faturayı silmek için
```

### 5.2 API Kimlik Doğrulama

API'lere erişim, JWT (JSON Web Token) tabanlı kimlik doğrulama kullanılarak korunmaktadır. Bir token almak için:

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username", "password":"your_password"}'
```

Dönen token'ı, sonraki API isteklerinde Authorization header'ında kullanın:

```bash
curl -X GET http://localhost:8000/api/crm/customers/ \
  -H "Authorization: Bearer <your_token>"
```

## 6. Frontend

### 6.1 Şablonlar

HTML şablonları, `templates/` dizininde bulunmaktadır. Şablonlar, Django'nun şablon sistemi kullanılarak oluşturulmuştur.

Ana şablon yapısı:

```
templates/
├── base.html              # Ana şablon
├── home.html              # Anasayfa şablonu
├── accounts/              # Hesap yönetimi şablonları
├── accounting/            # Muhasebe modülü şablonları
└── crm/                   # CRM modülü şablonları
```

### 6.2 Statik Dosyalar

CSS, JavaScript ve resim dosyaları, `static/` dizininde bulunmaktadır:

```
static/
├── css/
│   ├── styles.css         # Ana CSS dosyası
│   └── bootstrap.min.css  # Bootstrap CSS
├── js/
│   ├── app.js             # Ana JavaScript dosyası
│   ├── bootstrap.bundle.min.js  # Bootstrap JS
│   └── chart.js           # Chart.js kütüphanesi
└── img/                   # Resim dosyaları
```

### 6.3 Form İşleme

Django formları, kullanıcı girdilerini doğrulamak ve işlemek için kullanılır. Formlar, `apps/<app_name>/forms.py` dosyalarında tanımlanmıştır.

Örnek bir form:

```python
from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'tax_number', 'tax_office', 'address', 'phone', 'email', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_number': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_office': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
```

### 6.4 AJAX İstekleri

AJAX istekleri, dinamik içerik yüklemek ve form göndermek için kullanılır. Örnek bir AJAX isteği:

```javascript
// Müşteri listesini yükle
function loadCustomers() {
    $.ajax({
        url: '/api/crm/customers/',
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('token')
        },
        success: function(data) {
            // Müşteri listesini görüntüle
            renderCustomers(data);
        },
        error: function(xhr) {
            console.error('Müşteriler yüklenirken hata oluştu:', xhr.responseText);
        }
    });
}
```

## 7. Masaüstü Uygulaması

### 7.1 Masaüstü Uygulaması Yapısı

Masaüstü uygulaması, `desktop_app.py` dosyasında tanımlanmıştır. Uygulama, Tkinter kullanılarak bir GUI oluşturur ve yerel bir Django sunucusunu başlatır.

### 7.2 Masaüstü Uygulaması Derleme

Masaüstü uygulamasını derlemek için PyInstaller kullanılır. Derleme işlemi, `build_desktop.py` dosyasında tanımlanmıştır.

```bash
# Uygulamayı derle
python build_desktop.py
```

### 7.3 Çevrimdışı Çalışma Modu

Masaüstü uygulaması, çevrimdışı çalışma modunu destekler. Bu mod, verilerin yerel bir SQLite veritabanında saklanmasını ve daha sonra internete bağlanıldığında senkronize edilmesini sağlar.

## 8. Entegrasyonlar

### 8.1 E-Belge Entegrasyonu

FinAsis, e-Fatura ve e-Arşiv Fatura entegrasyonunu destekler. Entegrasyon, `apps/accounting/services/edocument_service.py` dosyasında tanımlanmıştır.

```python
class EDocumentService:
    def __init__(self, settings=None):
        self.settings = settings or self._get_default_settings()
        self.api_url = self.settings.get('api_url')
        self.api_key = self.settings.get('api_key')
        
    def create_e_invoice(self, invoice):
        # E-fatura oluşturma işlemi
        pass
        
    def send_e_invoice(self, invoice):
        # E-fatura gönderme işlemi
        pass
        
    def check_e_invoice_status(self, invoice):
        # E-fatura durumunu kontrol etme işlemi
        pass
        
    def cancel_e_invoice(self, invoice):
        # E-fatura iptal etme işlemi
        pass
```

### 8.2 Banka Entegrasyonu

FinAsis, banka entegrasyonunu destekler. Banka entegrasyonu, `apps/accounting/services/bank_service.py` dosyasında tanımlanmıştır.

```python
class BankService:
    def __init__(self, bank_settings):
        self.bank_settings = bank_settings
        self.api_url = bank_settings.get('api_url')
        self.api_key = bank_settings.get('api_key')
        
    def get_account_balance(self, account_number):
        # Hesap bakiyesini sorgulama
        pass
        
    def get_transactions(self, account_number, start_date, end_date):
        # Hesap hareketlerini sorgulama
        pass
        
    def make_transfer(self, from_account, to_account, amount, description):
        # Havale/EFT işlemi
        pass
```

## 9. Test

### 9.1 Birim Testleri

Birim testleri, `tests/` dizininde bulunmaktadır. Testleri çalıştırmak için:

```bash
# Tüm testleri çalıştır
python manage.py test

# Belirli bir uygulama için testleri çalıştır
python manage.py test apps.accounting

# Belirli bir test sınıfı için testleri çalıştır
python manage.py test apps.accounting.tests.test_invoice
```

### 9.2 Entegrasyon Testleri

Entegrasyon testleri, `pytest` kullanılarak yazılmıştır. Testleri çalıştırmak için:

```bash
# Tüm testleri çalıştır
pytest

# Belirli bir test dosyasını çalıştır
pytest tests/integration/test_edocument_service.py
```

### 9.3 Test Kapsamı

Test kapsamını kontrol etmek için:

```bash
# Test kapsamını html olarak raporla
pytest --cov=apps --cov-report=html
```

## 10. Dağıtım

### 10.1 Docker İle Dağıtım

FinAsis, Docker kullanılarak kolayca dağıtılabilir. Docker dosyaları:

- `Dockerfile`: Web uygulaması için
- `docker-compose.yml`: Web uygulaması, veritabanı ve diğer servisleri içerir

Docker ile dağıtım için:

```bash
# Docker imajı oluştur
docker build -t finasis:latest .

# Docker Compose ile çalıştır
docker-compose up -d
```

### 10.2 Manuel Dağıtım

Manuel dağıtım için:

1. Üretim sunucusuna kodu klonlayın veya kopyalayın
2. Gerekli bağımlılıkları yükleyin: `pip install -r requirements.txt`
3. Veritabanını oluşturun: `python manage.py migrate`
4. Statik dosyaları toplayın: `python manage.py collectstatic`
5. Gunicorn veya uWSGI ile web sunucusunu başlatın
6. Nginx veya Apache gibi bir ters proxy sunucusu ile uygulamayı sunun

### 10.3 Masaüstü Uygulaması Dağıtımı

Masaüstü uygulamasını dağıtmak için:

1. PyInstaller ile uygulamayı derleyin: `python build_desktop.py`
2. `dist/` dizinindeki `.exe` (Windows) veya uygulamayı dağıtın

## 11. Sorun Giderme ve Hata Ayıklama

### 11.1 Loglar

Loglar, `logs/` dizininde saklanır. Log seviyelerini ve formatını, `config/settings/base.py` dosyasında yapılandırabilirsiniz.

### 11.2 Django Debug Toolbar

Geliştirme ortamında, Django Debug Toolbar etkindir. Bu araç, SQL sorgularını, şablon oluşturma süresini ve diğer performans metriklerini görüntülemenize yardımcı olur.

### 11.3 Hata Takibi

Üretim ortamında oluşan hataları takip etmek için Sentry entegrasyonu kullanılmaktadır. Sentry ayarları, `config/settings/prod.py` dosyasında yapılandırılabilir.

## 12. Sürüm Yönetimi

### 12.1 Sürüm Numaralandırma

FinAsis, Semantic Versioning (SemVer) ilkelerini takip eder:

- **MAJOR.MINOR.PATCH** (örn. 1.2.3)
- **MAJOR**: Önemli değişiklikler ve geriye dönük uyumsuz API değişiklikleri
- **MINOR**: Yeni özellikler (geriye dönük uyumlu)
- **PATCH**: Hata düzeltmeleri ve küçük iyileştirmeler

### 12.2 Değişiklik Günlüğü

Tüm önemli değişiklikler, `CHANGELOG.md` dosyasında belgelenir. Değişiklik günlüğü, [Keep a Changelog](https://keepachangelog.com/) formatını takip eder.

### 12.3 Git İş Akışı

Geliştirme iş akışı:

1. Her özellik veya hata düzeltmesi için yeni bir dal oluşturun
2. Değişiklikleri yapın ve birleştirme isteği oluşturun
3. Kod incelemesi sonrası, değişiklikleri ana dala birleştirin

---

Bu dokümantasyon, FinAsis projesinin teknik yapısını, geliştirme sürecini ve bakım prosedürlerini kapsamaktadır. Daha fazla bilgi için, lütfen kodu inceleyin veya sorularınız için geliştirici ekibimize ulaşın.

*Son güncelleme: 20.04.2025* 