# FinAsis Analitik Modülü

## Genel Bakış

FinAsis analitik modülü, finansal verilerin görselleştirilmesi ve analizi için kapsamlı bir dashboard sistemi sunar.

## Özellikler

- Özelleştirilebilir dashboard'lar
- Çeşitli widget tipleri (grafikler, tablolar, metrikler)
- Gerçek zamanlı veri güncelleme
- Veri kaynağı entegrasyonu
- Raporlama sistemi

## Widget Tipleri

### 1. Çizgi Grafik
Zaman serisi verilerini görselleştirmek için kullanılır.

```python
settings = {
    'date_column': 'tarih',
    'value_columns': ['satis', 'gelir'],
    'colors': {
        'satis': '#2193B0',
        'gelir': '#6DD5ED'
    }
}
```

### 2. Sütun Grafik
Kategorik verileri karşılaştırmak için kullanılır.

```python
settings = {
    'label_column': 'urun',
    'value_column': 'satis',
    'title': 'Ürün Satışları',
    'color': '#2193B0'
}
```

### 3. Pasta Grafik
Oranları ve dağılımları göstermek için kullanılır.

```python
settings = {
    'label_column': 'kategori',
    'value_column': 'oran',
    'colors': ['#FF6B6B', '#4ECDC4', '#FFEEAD', '#96CEB4']
}
```

### 4. Tablo
Detaylı veri gösterimi için kullanılır.

```python
settings = {
    'columns': ['urun', 'satis', 'gelir', 'kar']
}
```

### 5. Metrik
Önemli KPI'ları göstermek için kullanılır.

```python
settings = {
    'value_column': 'kar',
    'title': 'Toplam Kar',
    'prefix': '₺',
    'suffix': ''
}
```

### 6. Gösterge
Performans göstergeleri için kullanılır.

```python
settings = {
    'value_column': 'performans',
    'min_value': 0,
    'max_value': 100,
    'zones': [
        {'strokeStyle': "#F03E3E", 'min': 0, 'max': 20},
        {'strokeStyle': "#FFDD00", 'min': 20, 'max': 60},
        {'strokeStyle': "#30B32D", 'min': 60, 'max': 100}
    ]
}
```

## API Endpoint'leri

### Dashboard
- `GET /analytics/dashboard/<int:dashboard_id>/` - Dashboard görünümü
- `GET /analytics/api/widget/<int:widget_id>/data/` - Widget verisi
- `POST /analytics/api/widget/<int:widget_id>/settings/` - Widget ayarları

### Raporlar
- `POST /analytics/api/reports/create/` - Yeni rapor oluştur
- `GET /analytics/api/reports/<int:report_id>/data/` - Rapor verisi

### Veri Kaynakları
- `POST /analytics/api/data-sources/add/` - Yeni veri kaynağı ekle
- `GET /analytics/api/data-sources/<int:source_id>/sync/` - Veri kaynağını senkronize et

## Hata Kodları

- `permission_denied` (403) - Yetkisiz erişim
- `rate_limit_exceeded` (429) - İstek limiti aşıldı
- `internal_error` (500) - Sunucu hatası

## Rate Limiting

API endpoint'leri için rate limiting uygulanmıştır:
- Maksimum istek: 60/dakika
- Zaman penceresi: 60 saniye

## Güvenlik

- Tüm API endpoint'leri kimlik doğrulaması gerektirir
- HTTPS zorunludur
- Rate limiting uygulanmıştır
- Veri erişim kontrolleri mevcuttur 