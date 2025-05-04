# FinAsis Canlıya Alma Kontrol Listesi

## Deployment Öncesi Kontroller

- [ ] Tüm testler başarılı
- [ ] DEBUG = False olarak ayarlandı
- [ ] SECRET_KEY güvenli ve ortama özgü
- [ ] ALLOWED_HOSTS doğru yapılandırıldı
- [ ] Veritabanı yedeklendi
- [ ] requirements.txt güncel
- [ ] .env.prod dosyası hazır ve güvenli
- [ ] SSL sertifikaları güncel
- [ ] static/ ve media/ dizinleri hazır
- [ ] Disk alanı yeterli

## Deployment Sonrası Kontroller

- [ ] Site https:// üzerinden erişilebilir
- [ ] Admin paneli çalışıyor
- [ ] Kullanıcı girişi çalışıyor
- [ ] Veritabanı migrasyonları tamam
- [ ] Statik dosyalar yüklendi
- [ ] E-posta gönderimi çalışıyor
- [ ] Oyun modülleri çalışıyor
- [ ] Sağlık kontrolü başarılı
- [ ] Loglar düzgün tutuluyor
- [ ] Yedekleme sistemi aktif

## Rollback Planı

1. Son çalışan versiyonun yedeğini al
2. Veritabanını yedekten geri yükle
3. Kod tabanını önceki sürüme döndür
4. Servisleri yeniden başlat
5. Sistemi test et

## Önemli Komutlar

```bash
# Deployment başlatma
./deploy.sh

# Log izleme
docker-compose -f docker-compose.prod.yml logs -f

# Servis durumu
docker-compose -f docker-compose.prod.yml ps

# Yedek alma
./backup.sh

# Rollback
./rollback.sh
```
