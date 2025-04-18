# MVT Dönüşümü Sonrası Model ve Kod Düzeltme Rehberi

Bu belge, MVT yapısına dönüşüm sonrası modellerde ve kodlarda yapılması gereken değişiklikleri açıklar.

## 1. Import İfadelerini Düzeltme

### Birleştirilen Modüller için Import Değişiklikleri

| Eski Import | Yeni Import |
|-------------|-------------|
| `from crm import ...` | `from apps.crm import ...` |
| `from customers import ...` | `from apps.crm import ...` |
| `from users import ...` | `from apps.hr_management import ...` |
| `from assets import ...` | `from apps.stock_management import ...` |
| `from inventory import ...` | `from apps.stock_management import ...` |
| `from efatura import ...` | `from apps.integrations.efatura import ...` |
| `from bank_integration import ...` | `from apps.integrations.bank_integration import ...` |
| `from ext_services import ...` | `from apps.integrations.services import ...` |
| `from external_integrations import ...` | `from apps.integrations.external import ...` |

### Özellikle Dikkat Edilmesi Gereken İmport İfadeleri

```python
# Eski
from customers.models import Customer, CustomerDocument, CustomerNote
from users.models import User

# Yeni
from apps.crm.models import Customer, CustomerDocument, CustomerNote
from apps.hr_management.models import User
```

## 2. Model Düzeltmeleri

### 2.1. ForeignKey ve İlişkilerde Değişiklikler

ForeignKey, ManyToMany ve OneToOne ilişkilerinde model referanslarının güncellenmesi gerekiyor:

```python
# Eski
customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE)
user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

# Yeni
customer = models.ForeignKey('apps.crm.Customer', on_delete=models.CASCADE)
user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
```

### 2.2. Meta Sınıf ve Verbose Name Değişiklikleri

Meta sınıflarında tutarlılık olması için:

```python
# Recommended
class Meta:
    verbose_name = 'Müşteri'
    verbose_name_plural = 'Müşteriler'
    ordering = ['-created_at']
```

### 2.3. Çakışan Modeller İçin Düzeltmeler

CRM ve Customers modüllerinde benzer isimde modeller varsa (ör. Customer), bunlar birleştirilip tek modele dönüştürülmeli:

```python
# CRM ve Customers içindeki benzer modeller birleştirildi
class Customer(models.Model):
    """Müşteri modeli"""
    name = models.CharField(max_length=200, verbose_name='Müşteri Adı')
    email = models.EmailField(verbose_name='E-posta')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    # Diğer alanlar...
```

## 3. ViewSet ve View Düzeltmeleri

API ViewSet ve View sınıflarında import değişiklikleri yapılmalı:

```python 
# Eski
from customers.models import Customer
from customers.serializers import CustomerSerializer

# Yeni
from apps.crm.models import Customer
from apps.crm.serializers import CustomerSerializer
```

## 4. URL Yapısında Düzeltmeler

`urls.py` dosyalarında include işlemleri güncellenmeli:

```python
# Eski
path('customers/', include('customers.urls')),

# Yeni
path('customers/', include('apps.crm.urls')),
```

## 5. Template Dosyaları ve Statik Dosyalar

Template referansları ve statik dosya yolları güncellenmeli:

```python
# Template dosyalarında import dizini güncellemeleri
{% extends 'crm/base.html' %}  # 'customers/base.html' değil
```

## 6. Migration İşlemleri

Migrasyon sorunlarını çözmek için şu adımları izleyin:

1. `scripts/migration_fix.py` betiğini çalıştırın
2. `python manage.py makemigrations` ile yeni migrasyonlar oluşturun
3. `python scripts/apply_migrations.py` ile migrasyonları uygulayın

## 7. Geriye Dönük Uyumluluk İçin İpuçları

Eğer sistemde başka bağımlılıklar varsa, şu adımlar uygulanabilir:

1. Geçici olarak ilgili modüllere yönlendirme proxy modelleri eklenebilir
2. İmport edilecek modüller için eski yollardan `ImportError` yakalama mekanizması kurulabilir

## 8. Test İşlemleri

Tüm değişikliklerden sonra test etmek için:

1. `python manage.py check` ile hata kontrolü
2. `python manage.py test` ile testleri çalıştırma
3. API endpoint'leri ve temel fonksiyonları manuel test etme

## 9. Hata Durumları ve Çözümleri

| Hata | Çözüm |
|------|-------|
| `ModuleNotFoundError: No module named 'customers'` | İlgili import'ları `apps.crm` olarak güncelleyin |
| `AppRegistryNotReady: Apps aren't loaded yet` | Uygulama başlatma sırasını kontrol edin |
| `django.db.utils.ProgrammingError: relation does not exist` | Migrasyonları `--fake-initial` ile çalıştırın |
| `Reverse for 'customer_detail' not found` | URL adlarını ve namespace'leri kontrol edin |

## 10. Kontrol Listesi

- [ ] Tüm import ifadeleri düzeltildi
- [ ] Model referansları güncellendi
- [ ] Migrasyonlar yeni yapıya göre düzenlendi
- [ ] URL yapısı ve include ifadeleri güncellendi
- [ ] Şablonlar ve statik dosya yolları kontrol edildi
- [ ] Testler ve uygulama doğru çalışıyor 