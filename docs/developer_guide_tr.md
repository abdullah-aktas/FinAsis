# FinAsis Geliştirici Rehberi

Bu rehber, FinAsis projesinin geliştirilmesi için teknik dokümantasyonu içerir.

## İçindekiler

1. [Geliştirme Ortamı](#geliştirme-ortamı)
2. [Proje Yapısı](#proje-yapısı)
3. [Kod Standartları](#kod-standartları)
4. [API Geliştirme](#api-geliştirme)
5. [Veritabanı İşlemleri](#veritabanı-işlemleri)
6. [Test Yazımı](#test-yazımı)
7. [Dağıtım Süreci](#dağıtım-süreci)
8. [Hata Ayıklama](#hata-ayıklama)

## Geliştirme Ortamı

### Gereksinimler

- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Node.js 14+
- Docker & Docker Compose

### Kurulum

```bash
# Projeyi klonlayın
git clone https://github.com/finasis/finasis.git
cd finasis

# Sanal ortam oluşturun
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Bağımlılıkları yükleyin
pip install -r requirements.txt
npm install

# Ortam değişkenlerini ayarlayın
cp .env.example .env
# .env dosyasını düzenleyin

# Veritabanını oluşturun
python manage.py migrate

# Geliştirme sunucusunu başlatın
python manage.py runserver
```

### Docker ile Kurulum

```bash
# Geliştirme ortamı
docker-compose up -d

# Üretim ortamı
docker-compose -f docker-compose.prod.yml up -d
```

## Proje Yapısı

```
finasis/
├── apps/                    # Uygulama modülleri
│   ├── core/               # Çekirdek modül
│   ├── finance/            # Finans modülü
│   ├── accounting/         # Muhasebe modülü
│   ├── pwa/               # Progressive Web App
│   ├── ai_assistant/      # Yapay zeka asistanı
│   ├── analytics/         # Analitik modülü
│   ├── integrations/      # Entegrasyonlar
│   └── api/               # API endpoints
├── docs/                   # Dokümantasyon
├── locale/                # Dil dosyaları
├── static/                # Statik dosyalar
├── templates/             # HTML şablonları
├── tests/                 # Test dosyaları
├── .env.example          # Örnek ortam değişkenleri
├── docker-compose.yml    # Docker yapılandırması
├── Dockerfile            # Docker imaj yapılandırması
├── manage.py             # Django yönetim betiği
└── requirements.txt      # Python bağımlılıkları
```

## Kod Standartları

### Python Kod Standartları

- PEP 8 standartlarına uyun
- Docstring kullanın
- Type hinting kullanın
- Birim testler yazın

```python
from typing import List, Optional

def calculate_total(items: List[dict], discount: Optional[float] = None) -> float:
    """
    Toplam tutarı hesaplar.

    Args:
        items: Ürün listesi
        discount: İndirim oranı (opsiyonel)

    Returns:
        float: Toplam tutar
    """
    total = sum(item['price'] for item in items)
    if discount:
        total *= (1 - discount)
    return total
```

### JavaScript Kod Standartları

- ESLint kurallarına uyun
- JSDoc kullanın
- Modern JavaScript özelliklerini kullanın
- Birim testler yazın

```javascript
/**
 * Toplam tutarı hesaplar
 * @param {Array<Object>} items - Ürün listesi
 * @param {number} [discount] - İndirim oranı
 * @returns {number} Toplam tutar
 */
const calculateTotal = (items, discount) => {
  let total = items.reduce((sum, item) => sum + item.price, 0);
  if (discount) {
    total *= (1 - discount);
  }
  return total;
};
```

## API Geliştirme

### API Endpoint Oluşturma

```python
# views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Invoice
from .serializers import InvoiceSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    """
    Fatura işlemleri için API endpoint'leri
    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Kullanıcıya ait faturaları filtreler
        """
        return self.queryset.filter(user=self.request.user)
```

### Serializer Oluşturma

```python
# serializers.py
from rest_framework import serializers
from .models import Invoice, InvoiceItem

class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['id', 'name', 'quantity', 'unit_price', 'vat_rate']

class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ['id', 'invoice_number', 'date', 'items', 'total_amount']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        invoice = Invoice.objects.create(**validated_data)
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        return invoice
```

## Veritabanı İşlemleri

### Model Oluşturma

```python
# models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Invoice(models.Model):
    """
    Fatura modeli
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50, unique=True)
    date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['date']),
        ]
```

### Migration Oluşturma

```bash
# Migration oluşturma
python manage.py makemigrations

# Migration uygulama
python manage.py migrate

# Migration durumu
python manage.py showmigrations
```

## Test Yazımı

### Unit Test

```python
# tests/test_invoice.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Invoice

User = get_user_model()

class InvoiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.invoice = Invoice.objects.create(
            user=self.user,
            invoice_number='TEST001',
            date='2024-01-01',
            total_amount=1000.00
        )

    def test_invoice_creation(self):
        self.assertEqual(self.invoice.invoice_number, 'TEST001')
        self.assertEqual(self.invoice.total_amount, 1000.00)

    def test_invoice_user_relation(self):
        self.assertEqual(self.invoice.user, self.user)
```

### API Test

```python
# tests/test_api.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

class InvoiceAPITests(APITestCase):
    def setUp(self):
        # Test kullanıcısı oluştur
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_invoice(self):
        url = reverse('invoice-list')
        data = {
            'invoice_number': 'TEST001',
            'date': '2024-01-01',
            'total_amount': 1000.00,
            'items': [
                {
                    'name': 'Test Item',
                    'quantity': 1,
                    'unit_price': 1000.00,
                    'vat_rate': 18
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
```

## Dağıtım Süreci

### Geliştirme Ortamı

```bash
# Statik dosyaları topla
python manage.py collectstatic

# Geliştirme sunucusunu başlat
python manage.py runserver
```

### Üretim Ortamı

```bash
# Docker ile dağıtım
docker-compose -f docker-compose.prod.yml up -d

# Manuel dağıtım
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn finasis.wsgi:application
```

## Hata Ayıklama

### Logging

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Debug Toolbar

```python
# settings.py
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']
```

### Hata İzleme

```python
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import traceback

@csrf_exempt
def error_handler(request):
    try:
        # Kod burada
        pass
    except Exception as e:
        # Hatayı logla
        logger.error(f"Hata: {str(e)}\n{traceback.format_exc()}")
        return JsonResponse({
            'error': 'Bir hata oluştu',
            'detail': str(e) if DEBUG else None
        }, status=500)
```

---

Bu dokümantasyon, FinAsis projesinin teknik yapısını, geliştirme sürecini ve bakım prosedürlerini kapsamaktadır. Daha fazla bilgi için, lütfen kodu inceleyin veya sorularınız için geliştirici ekibimize ulaşın.

*Son güncelleme: 20.04.2025* 