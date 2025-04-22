# FinAsis Sistem Gereksinimleri

*Son Güncelleme: 22.04.2025*

## 🖥️ Donanım Gereksinimleri

### Minimum Gereksinimler
- **İşlemci**: 2 çekirdekli, 2.0 GHz veya üzeri
- **RAM**: 4 GB
- **Depolama**: 20 GB boş alan
- **Ağ**: 10 Mbps internet bağlantısı

### Önerilen Gereksinimler
- **İşlemci**: 4 çekirdekli, 3.0 GHz veya üzeri
- **RAM**: 8 GB
- **Depolama**: 50 GB boş alan (SSD önerilir)
- **Ağ**: 100 Mbps internet bağlantısı

## 💾 Yazılım Gereksinimleri

### Sunucu Tarafı
- **İşletim Sistemi**: 
  - Ubuntu 20.04 LTS veya üzeri
  - CentOS 8 veya üzeri
  - Windows Server 2019 veya üzeri
- **Python**: 3.9 veya üzeri
- **PostgreSQL**: 13 veya üzeri
- **Redis**: 6.0 veya üzeri
- **Node.js**: 14 veya üzeri
- **Nginx**: 1.18 veya üzeri

### İstemci Tarafı
- **İşletim Sistemi**:
  - Windows 10 veya üzeri
  - macOS 10.15 veya üzeri
  - Linux (Ubuntu 20.04 veya üzeri)
- **Tarayıcılar**:
  - Chrome 90 veya üzeri
  - Firefox 88 veya üzeri
  - Safari 14 veya üzeri
  - Edge 90 veya üzeri

## 🐳 Docker Gereksinimleri

### Docker Engine
- **Docker**: 20.10 veya üzeri
- **Docker Compose**: 2.0 veya üzeri

### Konteyner Gereksinimleri
- **CPU**: 2 çekirdek
- **RAM**: 4 GB
- **Depolama**: 30 GB

## 📱 Mobil Gereksinimler

### Android
- Android 8.0 veya üzeri
- 2 GB RAM
- 100 MB boş alan

### iOS
- iOS 13 veya üzeri
- 2 GB RAM
- 100 MB boş alan

## 🔒 Güvenlik Gereksinimleri

- SSL/TLS sertifikası
- Güvenlik duvarı yapılandırması
- Düzenli yedekleme sistemi
- Antivirüs yazılımı
- Güvenlik güncellemelerinin düzenli uygulanması

## 🌐 Ağ Gereksinimleri

### Gerekli Portlar
- 80 (HTTP)
- 443 (HTTPS)
- 5432 (PostgreSQL)
- 6379 (Redis)
- 8000 (Geliştirme sunucusu)

### Ağ Bant Genişliği
- Minimum: 10 Mbps
- Önerilen: 100 Mbps
- Yedekleme için: 1 Gbps

## 📊 Veritabanı Gereksinimleri

### PostgreSQL
- Sürüm: 13 veya üzeri
- Depolama: Veri boyutunun 2 katı
- RAM: Toplam veri boyutunun %25'i
- CPU: 2 çekirdek

### Redis
- Sürüm: 6.0 veya üzeri
- RAM: 1 GB
- Kalıcı depolama: 2 GB

## 🔄 Yedekleme Gereksinimleri

- Günlük tam yedekleme
- Saatlik artırımlı yedekleme
- Yedeklerin farklı lokasyonda saklanması
- Minimum 30 günlük yedek saklama süresi

## 📈 Ölçeklenebilirlik

### Küçük Ölçek (10 kullanıcı)
- 2 CPU çekirdeği
- 4 GB RAM
- 50 GB depolama

### Orta Ölçek (50 kullanıcı)
- 4 CPU çekirdeği
- 8 GB RAM
- 100 GB depolama

### Büyük Ölçek (200+ kullanıcı)
- 8 CPU çekirdeği
- 16 GB RAM
- 500 GB depolama
- Yük dengeleme
- Çoklu sunucu dağıtımı 