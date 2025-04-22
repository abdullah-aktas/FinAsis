# FinAsis Geliştirici Kılavuzu

*Son Güncelleme: 22.04.2025*

## 📋 Genel Bakış

Bu kılavuz, FinAsis uygulamasına katkıda bulunmak isteyen geliştiriciler için hazırlanmıştır.

## 🔧 Geliştirme Ortamı

### Gereksinimler
- Python 3.9+
- Node.js 14+
- Docker 20.10+
- Git 2.30+
- IDE (VS Code, PyCharm vb.)

### Ortam Kurulumu
```bash
# Projeyi klonla
git clone https://github.com/finasis/finasis.git
cd finasis

# Sanal ortam oluştur
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Bağımlılıkları yükle
pip install -r requirements/dev.txt
npm install
```

## 📚 Kod Standartları

### Python
- PEP 8 standartlarına uyun
- Black formatter kullanın
- Flake8 linter kullanın
- Docstring'leri Google formatında yazın

### JavaScript
- ESLint kurallarına uyun
- Prettier formatter kullanın
- JSDoc formatında dokümantasyon yazın

### Git
- Semantic commit mesajları kullanın
- Feature branch workflow'u takip edin
- Pull request'lerde detaylı açıklama yazın

## 🛠️ Geliştirme Süreci

### 1. Branch Oluşturma
```bash
git checkout -b feature/new-feature
```

### 2. Kod Yazma
```python
def example_function(param1: str, param2: int) -> bool:
    """Örnek fonksiyon açıklaması.

    Args:
        param1: İlk parametre açıklaması
        param2: İkinci parametre açıklaması

    Returns:
        bool: Dönüş değeri açıklaması
    """
    return True
```

### 3. Test Yazma
```python
def test_example_function():
    """Test fonksiyonu açıklaması."""
    assert example_function("test", 1) is True
```

### 4. Kod İnceleme
```bash
# Linter çalıştır
flake8
eslint .

# Testleri çalıştır
pytest
npm test
```

## 📦 Modül Geliştirme

### 1. Yeni Modül Oluşturma
```bash
python manage.py startapp new_module
```

### 2. Modül Yapısı
```
new_module/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── views.py
├── urls.py
├── serializers.py
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   └── test_serializers.py
└── templates/
    └── new_module/
```

### 3. API Endpoint Ekleme
```python
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/new-module/', views.NewModuleView.as_view()),
]
```

## 🔍 Debugging

### 1. Loglama
```python
import logging

logger = logging.getLogger(__name__)

def example_function():
    logger.debug("Debug mesajı")
    logger.info("Bilgi mesajı")
    logger.warning("Uyarı mesajı")
    logger.error("Hata mesajı")
```

### 2. Breakpoint Kullanımı
```python
def example_function():
    import pdb; pdb.set_trace()  # Python debugger
    # veya
    breakpoint()  # Python 3.7+
```

## 📊 Performans Optimizasyonu

### 1. Veritabanı Optimizasyonu
```python
# N+1 sorgu problemi çözümü
queryset = Model.objects.select_related('related_field')
queryset = Model.objects.prefetch_related('many_related_field')
```

### 2. Önbellekleme
```python
from django.core.cache import cache

@cache_page(60 * 15)  # 15 dakika önbellekleme
def cached_view(request):
    return HttpResponse("Önbelleklenmiş içerik")
```

### 3. Asenkron İşlemler
```python
from celery import shared_task

@shared_task
def async_task(param1, param2):
    # Uzun süren işlem
    return result
```

## 🔒 Güvenlik

### 1. Güvenlik Kontrolleri
```python
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

@login_required
def protected_view(request):
    return HttpResponse("Korumalı içerik")

class ProtectedView(LoginRequiredMixin, View):
    def get(self, request):
        return HttpResponse("Korumalı içerik")
```

### 2. Veri Doğrulama
```python
from django.core.exceptions import ValidationError

def clean_data(data):
    if not data.get('required_field'):
        raise ValidationError("Bu alan zorunludur")
    return data
```

## 📚 Dokümantasyon

### 1. Kod Dokümantasyonu
```python
def documented_function(param1, param2):
    """Fonksiyon açıklaması.

    Args:
        param1: İlk parametre açıklaması
        param2: İkinci parametre açıklaması

    Returns:
        Dönüş değeri açıklaması

    Raises:
        ValueError: Hata durumu açıklaması
    """
    pass
```

### 2. API Dokümantasyonu
```python
from drf_yasg import openapi

@swagger_auto_schema(
    operation_description="API endpoint açıklaması",
    responses={200: "Başarılı yanıt açıklaması"}
)
def api_view(request):
    pass
```

## 🤝 Katkıda Bulunma

### 1. Pull Request Süreci
1. Fork oluştur
2. Feature branch oluştur
3. Değişiklikleri commit et
4. Pull request aç
5. Code review bekle
6. Değişiklikleri birleştir

### 2. Code Review Kuralları
- Kod standartlarına uygunluk
- Test coverage
- Performans etkisi
- Güvenlik kontrolleri
- Dokümantasyon tamlığı

## 📞 Destek

### İletişim
- E-posta: dev-support@finasis.com
- Slack: #dev-support
- GitHub Issues

### SLA
- Yanıt süresi: 24 saat
- Çözüm süresi: 72 saat
- Code review süresi: 48 saat 