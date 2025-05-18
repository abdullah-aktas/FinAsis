# FinAsis Felaket Kurtarma Planı

## 1. Giriş

Bu doküman, FinAsis uygulamasının felaket durumlarında kurtarma prosedürlerini detaylandırmaktadır. Felaket durumları şunları içerebilir:
- Veritabanı çökmesi
- Sunucu arızası
- Doğal afetler
- Siber saldırılar
- İnsan kaynaklı hatalar

## 2. Yedekleme Stratejisi

### 2.1 Veritabanı Yedekleri
- Günlük tam yedekleme (Her gün saat 02:00'de)
- Saatlik artırımlı yedekleme
- Yedekler Google Cloud Storage'da saklanır
- Yedekler 30 gün boyunca tutulur
- Yedekleme script'i: `scripts/backup.py`

### 2.2 Media Dosyaları
- Günlük tam yedekleme (Her gün saat 03:00'de)
- Yedekler Google Cloud Storage'da saklanır
- Yedekler 30 gün boyunca tutulur
- Yedekleme script'i: `scripts/backup.py`

### 2.3 Kod Deposu
- GitHub'da ana depo
- Günlük yerel yedekleme
- Tüm branch'ler ve tag'ler yedeklenir

## 3. Kurtarma Prosedürleri

### 3.1 Veritabanı Kurtarma
1. Yedek dosyasını seç
2. Mevcut veritabanı bağlantılarını sonlandır
3. Veritabanını geri yükle:
```bash
python scripts/backup.py --restore-db <backup_file>
```
4. Veritabanı bütünlüğünü kontrol et
5. Uygulamayı yeniden başlat

### 3.2 Media Dosyaları Kurtarma
1. Yedek dosyasını seç
2. Mevcut media dosyalarını yedekle
3. Media dosyalarını geri yükle:
```bash
python scripts/backup.py --restore-media <backup_file>
```
4. Dosya izinlerini kontrol et
5. Uygulamayı yeniden başlat

### 3.3 Sunucu Kurtarma
1. Yeni sunucu oluştur
2. DNS kayıtlarını güncelle
3. SSL sertifikalarını yenile
4. Uygulamayı deploy et
5. Veritabanı ve media dosyalarını geri yükle
6. Uygulamayı başlat

## 4. İletişim Planı

### 4.1 Acil Durum İletişim Listesi
- Teknik Ekip: tech@finasis.com.tr
- Yönetici: manager@finasis.com.tr
- Müşteri Desteği: support@finasis.com.tr

### 4.2 Müşteri İletişimi
- Durum sayfası: status.finasis.com.tr
- E-posta bildirimleri
- SMS bildirimleri

## 5. Test ve Bakım

### 5.1 Yedekleme Testleri
- Aylık yedekleme testi
- Geri yükleme testi
- Bütünlük kontrolü

### 5.2 Felaket Kurtarma Tatbikatı
- Üç ayda bir tatbikat
- Senaryo bazlı testler
- Dokümantasyon güncelleme

## 6. Güvenlik Önlemleri

### 6.1 Erişim Kontrolü
- Yedeklere erişim kısıtlaması
- İki faktörlü doğrulama
- IP kısıtlamaları

### 6.2 Şifreleme
- Yedekler Google Cloud Storage'ın varsayılan şifrelemesi ile korunur
- SSL/TLS kullanımı
- Güvenli anahtar yönetimi

## 7. Dokümantasyon ve Eğitim

### 7.1 Dokümantasyon
- Bu plan düzenli olarak güncellenir
- Tüm değişiklikler kaydedilir
- Versiyon kontrolü yapılır

### 7.2 Eğitim
- Yeni ekip üyeleri için eğitim
- Düzenli tekrar eğitimleri
- Tatbikat sonrası değerlendirme

## 8. İzleme ve Raporlama

### 8.1 İzleme
- Yedekleme başarısı
- Disk kullanımı
- Google Cloud Storage kullanımı

### 8.2 Raporlama
- Aylık yedekleme raporu
- Felaket kurtarma tatbikat raporu
- Olay raporları

## 9. Yasal Gereklilikler

### 9.1 Veri Saklama
- KVKK uyumluluğu
- Mali kayıtların saklanması
- E-belge saklama süreleri

### 9.2 Sorumluluklar
- Veri sorumlusu
- Teknik ekip
- Yönetici

## 10. Güncellemeler

### 10.1 Plan Güncellemeleri
- Son güncelleme: [TARİH]
- Bir sonraki gözden geçirme: [TARİH]
- Güncelleyen: [İSİM]

### 10.2 Değişiklik Geçmişi
- [TARİH] - İlk versiyon
- [TARİH] - AWS S3'ten Google Cloud Storage'a geçiş
- [TARİH] - Güncelleme 2 