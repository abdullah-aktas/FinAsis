# FinAsis - Finansal Yönetim Sistemi

FinAsis, modern ve kapsamlı bir finansal yönetim sistemidir. Kurumsal finans yönetimi, muhasebe, CRM ve blockchain entegrasyonu gibi özellikleri içeren kapsamlı bir çözüm sunar.

## Özellikler

- Kullanıcı Yönetimi ve Güvenlik
  - Çoklu dil desteği (Türkçe, İngilizce, Almanca, Arapça, Kürtçe)
  - İki faktörlü kimlik doğrulama
  - Rol tabanlı yetkilendirme
  - Oturum yönetimi

- Finansal Yönetim
  - Muhasebe modülü
  - Bütçe planlama ve takip
  - Finansal raporlama
  - Blockchain entegrasyonu

- CRM ve Müşteri Yönetimi
  - Müşteri portföyü yönetimi
  - İletişim takibi
  - Görev ve hatırlatıcılar

- Mobil Uygulama
  - iOS ve Android desteği
  - Anlık bildirimler
  - Offline çalışma modu

## Kurulum

### Gereksinimler

- Python 3.8 veya üzeri
- PostgreSQL 12 veya üzeri
- Redis (önbellek ve mesaj kuyruğu için)
- Node.js (frontend geliştirme için)

### Kurulum Adımları

1. Projeyi klonlayın:
```bash
git clone https://github.com/abdullah-aktas/FinAsis.git
cd FinAsis
```

2. Sanal ortam oluşturun ve aktifleştirin:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

4. Veritabanını oluşturun:
```bash
python manage.py migrate
```

5. Geliştirme sunucusunu başlatın:
```bash
python manage.py runserver
```

## Kullanım Kılavuzu

Detaylı kullanım kılavuzu için [docs](docs/) klasörüne bakın:
- [Kullanıcı Kılavuzu](docs/user_guide.md)
- [Yönetici Kılavuzu](docs/admin_guide.md)
- [API Dokümantasyonu](docs/api_documentation.md)

## Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## İletişim

- Proje Yöneticisi: [Abdullah Aktaş](mailto:abdullah.aktas@example.com)
- Web Sitesi: [https://finasis.com.tr](https://finasis.com.tr)
