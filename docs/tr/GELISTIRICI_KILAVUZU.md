# FinAsis Geliştirici Kılavuzu

## İçindekiler
1. [Proje Yapısı](#proje-yapısı)
2. [Geliştirme Ortamı Kurulumu](#geliştirme-ortamı-kurulumu)
3. [Kod Standartları](#kod-standartları)
4. [Modül Geliştirme](#modül-geliştirme)
5. [Test Yazımı](#test-yazımı)
6. [Dağıtım Süreci](#dağıtım-süreci)

## Proje Yapısı

FinAsis, modüler bir yapıya sahip bir finans yönetim sistemidir. Ana bileşenler:

- `core/`: Çekirdek işlevsellik
- `api/`: API endpoints
- `backend/`: Backend servisleri
- `frontend/`: Kullanıcı arayüzü
- `modules/`: Özel modüller (CRM, Muhasebe, vb.)

## Geliştirme Ortamı Kurulumu

1. Python 3.8+ kurulumu
2. Node.js 14+ kurulumu
3. Gerekli bağımlılıkların kurulumu:
   ```bash
   pip install -r requirements.txt
   npm install
   ```
4. Veritabanı kurulumu
5. Geliştirme sunucusunun başlatılması

## Kod Standartları

- PEP 8 standartlarına uygun Python kodu
- ESLint kurallarına uygun JavaScript/TypeScript kodu
- Git commit mesajları için conventional commits
- Kod inceleme süreçleri

## Modül Geliştirme

1. Yeni modül oluşturma
2. Veritabanı modelleri
3. API endpoints
4. Frontend bileşenleri
5. Test yazımı

## Test Yazımı

- Unit testler
- Integration testler
- End-to-end testler
- Test coverage raporları

## Dağıtım Süreci

1. Kod inceleme
2. Test süreçleri
3. Staging ortamı
4. Production deployment
5. Monitoring ve logging 