# FinAsis - Finansal Yönetim ve Asistan Platformu

![FinAsis Logo](static/img/logo.png)

FinAsis, işletmelerin finansal yönetim, müşteri ilişkileri ve stok yönetimi süreçlerini dijitalleştirmesine yardımcı olan kapsamlı bir yazılım çözümüdür. Hem web uygulaması hem de masaüstü uygulaması olarak kullanılabilir.

## Özellikler

- **Muhasebe Yönetimi**: Hesap planı, faturalar, yevmiye kayıtları, vergi beyannameleri
- **Müşteri İlişkileri (CRM)**: Müşteri yönetimi, fırsat takibi, aktivite planlaması
- **E-Belge Entegrasyonu**: E-Fatura, E-Arşiv Fatura oluşturma ve yönetme
- **Stok Yönetimi**: Ürün kataloğu, stok giriş/çıkış işlemleri, sayım
- **Raporlama**: Mali tablolar, performans analizleri, iş zekası
- **Sanal Şirket Simülasyonu**: Eğitim amaçlı sanal şirket oluşturma ve yönetme
- **Masaüstü Uygulaması**: Çevrimiçi/çevrimdışı çalışma modu

## Kurulum

### Gereksinimler

- Python 3.9 veya üzeri
- pip (Python paket yöneticisi)
- SQLite veya PostgreSQL

### Web Uygulaması

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

5. Yönetici kullanıcısı oluşturun:
```bash
python manage.py createsuperuser
```

6. Geliştirme sunucusunu başlatın:
```bash
python manage.py runserver
```

7. Tarayıcınızda `http://127.0.0.1:8000` adresine giderek uygulamayı görüntüleyin.

### Masaüstü Uygulaması

#### Windows
```bash
scripts\build_and_run.bat
```

#### Linux/macOS
```bash
chmod +x scripts/build_and_run.sh
./scripts/build_and_run.sh
```

## Dokümantasyon

Detaylı dokümantasyon için `docs/` dizinine bakın:

- [Kullanım Kılavuzu](docs/user_manual_tr.md) - Kullanıcılar için rehber
- [Geliştirici Rehberi](docs/developer_guide_tr.md) - Geliştiriciler için teknik dokümantasyon

## Katkıda Bulunma

Projeye katkıda bulunmak isteyenler için adımlar:

1. Projeyi fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## İletişim

- Proje Websitesi: [https://finasis.com.tr](https://finasis.com.tr)
- E-posta: [info@finasis.com.tr](mailto:info@finasis.com.tr)
- Twitter: [@FinAsisTR](https://twitter.com/FinAsisTR)
- LinkedIn: [FinAsis](https://www.linkedin.com/company/finasis/)