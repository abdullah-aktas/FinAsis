# FinAsis Masaüstü Uygulaması Kullanıcı Kılavuzu

## İçindekiler
1. [Giriş](#giriş)
2. [Kurulum](#kurulum)
3. [Arayüz Tanıtımı](#arayüz-tanıtımı)
4. [Temel İşlemler](#temel-işlemler)
5. [Offline Mod](#offline-mod)
6. [Güncellemeler](#güncellemeler)
7. [Sorun Giderme](#sorun-giderme)

## Giriş

FinAsis Masaüstü Uygulaması, FinAsis web uygulamasının yerel bir sunucu üzerinde çalışmasını sağlayan bir arayüzdür. Bu uygulama sayesinde web uygulamasına internet bağlantısı olmadan da erişebilirsiniz.

## Kurulum

1. FinAsis Masaüstü Uygulaması kurulum dosyasını indirin
2. Kurulum dosyasını çalıştırın
3. Kurulum sihirbazını takip edin
4. Kurulum tamamlandığında uygulama otomatik olarak başlatılacaktır

## Arayüz Tanıtımı

### Ana Pencere
- **Başlık Çubuğu**: Uygulama adı ve menü çubuğu
- **Logo Alanı**: FinAsis logosu ve uygulama adı
- **Sunucu Durumu**: Sunucunun çalışma durumunu gösterir
- **Kontrol Butonları**: Sunucuyu başlatma, durdurma, tarayıcıda açma ve offline mod butonları
- **Sistem Bilgileri**: Uygulama versiyonu ve güncelleme durumu
- **Senkronizasyon Durumu**: Offline modda veri senkronizasyon durumu
- **Alt Bilgi**: Telif hakkı bilgisi

### Menü Çubuğu
- **Dosya Menüsü**
  - Ayarlar: Uygulama ayarlarını düzenleme
  - Çıkış: Uygulamadan çıkış yapma
- **Yardım Menüsü**
  - Kullanıcı Kılavuzu: Bu kılavuzu açma
  - Güncellemeleri Kontrol Et: Yeni güncellemeleri kontrol etme
  - Hakkında: Uygulama hakkında bilgi

## Temel İşlemler

### Sunucuyu Başlatma
1. "Sunucuyu Başlat" butonuna tıklayın
2. Sunucu başlatılırken ilerleme çubuğu görüntülenecektir
3. Sunucu başlatıldığında durum göstergesi yeşil olacaktır

### Tarayıcıda Açma
1. Sunucu çalışır durumdayken "Tarayıcıda Aç" butonuna tıklayın
2. Varsayılan tarayıcınızda FinAsis web uygulaması açılacaktır

### Sunucuyu Durdurma
1. "Sunucuyu Durdur" butonuna tıklayın
2. Sunucu durdurulduğunda durum göstergesi kırmızı olacaktır

## Offline Mod

### Offline Moda Geçiş
1. "Offline Mod" butonuna tıklayın
2. Uygulama offline moda geçecek ve yerel veritabanını kullanmaya başlayacaktır
3. İnternet bağlantısı olmadan da verilerinize erişebilirsiniz

### Veri Senkronizasyonu
- Offline modda yapılan değişiklikler yerel veritabanında saklanır
- İnternet bağlantısı sağlandığında otomatik olarak senkronize edilir
- Senkronizasyon durumu arayüzde görüntülenir

### Offline Moddan Çıkış
1. "Online Mod" butonuna tıklayın
2. Uygulama online moda geçecek ve sunucu ile senkronizasyon başlayacaktır

## Güncellemeler

### Otomatik Güncelleme Kontrolü
- Uygulama her başlatıldığında otomatik olarak güncellemeleri kontrol eder
- Yeni bir güncelleme varsa kullanıcıya bildirilir
- Güncellemeler arka planda indirilir ve kurulur

### Manuel Güncelleme Kontrolü
1. "Yardım" menüsüne tıklayın
2. "Güncellemeleri Kontrol Et" seçeneğini seçin
3. Güncelleme varsa kurulum sihirbazı başlatılır

## Sorun Giderme

### Sunucu Başlatılamıyor
1. Uygulamayı yeniden başlatın
2. Başka bir uygulamanın 8000 portunu kullanmadığından emin olun
3. Antivirüs yazılımınızın uygulamaya izin verdiğinden emin olun

### Tarayıcıda Açılmıyor
1. Sunucunun çalıştığından emin olun
2. Tarayıcınızın güncel olduğundan emin olun
3. Varsayılan tarayıcı ayarlarınızı kontrol edin

### Offline Mod Sorunları
1. Yerel veritabanı dosyasının bozulmadığından emin olun
2. Uygulamayı yeniden başlatın
3. Veri senkronizasyonu için internet bağlantısını kontrol edin

### Güncelleme Sorunları
1. İnternet bağlantınızı kontrol edin
2. Uygulamayı yönetici olarak çalıştırmayı deneyin
3. Antivirüs yazılımınızın güncelleme işlemine izin verdiğinden emin olun

## Log Dosyaları
- Uygulama logları `~/.finasis/logs` dizininde saklanır
- Her gün için ayrı bir log dosyası oluşturulur
- Hata durumlarında bu logları kontrol edin

## İletişim

Sorun yaşarsanız veya yardıma ihtiyacınız olursa:
- E-posta: support@finasis.com
- Telefon: +90 212 123 45 67
- Web: https://www.finasis.com/support 