# FinAsis Mobil Uygulaması

FinAsis'in mobil uygulaması Kivy framework'ü kullanılarak geliştirilmiştir.

## Kurulum

1. Python 3.8 veya üstü sürümünün yüklü olduğundan emin olun.

2. Sanal ortam oluşturun ve aktif edin:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac için
venv\Scripts\activate     # Windows için
```

3. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

4. Uygulamayı çalıştırın:
```bash
python main.py
```

## Özellikler

- Finansal özet grafikleri
- Muhasebe işlemleri
- Raporlama
- CRM entegrasyonu
- Ayarlar yönetimi

## Geliştirme

### Proje Yapısı

```
FinasisMobile/
├── main.py              # Ana uygulama dosyası
├── requirements.txt     # Bağımlılıklar
├── services/           # API servisleri
│   └── api.py
└── assets/            # Görseller ve diğer kaynaklar
```

### API Entegrasyonu

API servisleri `services/api.py` dosyasında tanımlanmıştır. Backend API'si ile iletişim için gerekli tüm metodlar burada bulunmaktadır.

## Dağıtım

### Android için APK Oluşturma

1. Buildozer'ı yükleyin:
```bash
pip install buildozer
```

2. Buildozer yapılandırmasını başlatın:
```bash
buildozer init
```

3. APK oluşturun:
```bash
buildozer android debug
```

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. 