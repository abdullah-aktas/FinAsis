# FinAsis Hızlı Başlangıç Kılavuzu

*Son Güncelleme: 22.04.2025*

## 🚀 Hızlı Başlangıç

Bu kılavuz, FinAsis'i hızlıca kurmanız ve kullanmaya başlamanız için gerekli adımları içerir.

### 1. Kurulum

#### Docker ile Kurulum (Önerilen)

```bash
# Projeyi klonlayın
git clone https://github.com/abdullah-aktas/FinAsis.git
cd FinAsis

# Docker ile başlatın
docker-compose up -d
```

#### Yerel Kurulum

```bash
# Python sanal ortamı oluşturun
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Veritabanını oluşturun
python manage.py migrate

# Yönetici kullanıcısı oluşturun
python manage.py createsuperuser
```

### 2. İlk Yapılandırma

1. Tarayıcınızda `http://localhost:8000` adresine gidin
2. Yönetici hesabınızla giriş yapın
3. Ayarlar menüsünden temel yapılandırmaları yapın:
   - Şirket bilgileri
   - Muhasebe ayarları
   - Kullanıcı izinleri

### 3. Temel İşlemler

#### Müşteri Ekleme
1. CRM > Müşteriler menüsüne gidin
2. "Yeni Müşteri" butonuna tıklayın
3. Müşteri bilgilerini girin ve kaydedin

#### Fatura Oluşturma
1. Muhasebe > Faturalar menüsüne gidin
2. "Yeni Fatura" butonuna tıklayın
3. Müşteri seçin ve fatura detaylarını girin
4. Kaydedin ve yazdırın

#### Stok Girişi
1. Stok > Ürünler menüsüne gidin
2. "Yeni Ürün" butonuna tıklayın
3. Ürün bilgilerini girin
4. Stok girişi yapın

### 4. İpuçları

- Yapay zeka asistanını kullanmak için sağ alt köşedeki asistan ikonuna tıklayın
- Mobil uygulamayı kullanmak için PWA özelliğini etkinleştirin
- Çoklu dil desteği için ayarlar menüsünden dil seçin

### 5. Sonraki Adımlar

- [Kullanıcı Kılavuzu](user_manual_tr.md) ile detaylı bilgi edinin
- [API Dokümantasyonu](api_documentation.md) ile entegrasyon yapın
- [Geliştirici Rehberi](developer_guide_tr.md) ile özelleştirme yapın

## 📞 Yardım

Sorularınız için:
- E-posta: support@finasis.com.tr
- Telefon: +90 850 123 4567
- Canlı Destek: Uygulama içi sohbet 