# FinAsis Deployment Prosedürü

## 🚀 Canlıya Geçiş Adımları

### 1. Ön Hazırlık
- [ ] Tüm testlerin başarılı olduğundan emin olun
- [ ] Code coverage %80'in üzerinde olmalı
- [ ] SonarQube'de kritik hata olmamalı
- [ ] Tüm bağımlılıklar güncel olmalı
- [ ] `.env.prod` dosyası hazır olmalı

### 2. Veritabanı Hazırlığı
```bash
# Veritabanı yedeği al
./scripts/backup.sh

# Migrations kontrol et
python manage.py showmigrations

# Migrations uygula
python manage.py migrate
```

### 3. Statik Dosyalar
```bash
# Statik dosyaları topla
python manage.py collectstatic --noinput

# AWS S3'e yükle (eğer kullanılıyorsa)
aws s3 sync staticfiles/ s3://finasis-static/
```

### 4. Docker Image Hazırlığı
```bash
# Image oluştur
docker build -t finasis:latest .

# DockerHub'a gönder
docker push finasis:latest
```

### 5. SSL Sertifikası
- [ ] SSL sertifikasının geçerlilik süresini kontrol et
- [ ] Let's Encrypt yenileme durumunu kontrol et
- [ ] Traefik SSL yapılandırmasını kontrol et

### 6. Monitoring & Logging
- [ ] Prometheus hedeflerini kontrol et
- [ ] Grafana dashboardlarını kontrol et
- [ ] Log rotasyonunu kontrol et
- [ ] Disk alanı kontrolü yap

### 7. Deployment
```bash
# Servisleri başlat
docker-compose -f docker-compose.prod.yml up -d

# Sağlık kontrolü
curl -f https://finasis.com.tr/health/

# Log kontrolü
docker-compose -f docker-compose.prod.yml logs -f
```

### 8. Post-Deployment Kontroller
- [ ] Tüm API endpoint'leri çalışıyor mu?
- [ ] Kullanıcı girişi çalışıyor mu?
- [ ] E-Fatura entegrasyonu çalışıyor mu?
- [ ] Oyun modülü çalışıyor mu?
- [ ] PDF oluşturma çalışıyor mu?
- [ ] Email gönderimi çalışıyor mu?

### 9. Performans Kontrolleri
- [ ] Response time < 2s
- [ ] CPU kullanımı < %80
- [ ] Memory kullanımı < %80
- [ ] Disk I/O normal seviyede
- [ ] Network I/O normal seviyede

### 10. Güvenlik Kontrolleri
- [ ] WAF aktif ve çalışıyor
- [ ] Rate limiting aktif
- [ ] HTTPS yönlendirmesi çalışıyor
- [ ] Security headers doğru ayarlanmış
- [ ] CSP kuralları aktif

## 🔄 Rollback Prosedürü
Eğer deployment sırasında kritik bir sorun çıkarsa:

```bash
# Son başarılı versiyona dön
./scripts/rollback.sh YYYYMMDD_HHMMSS

# Servisleri kontrol et
docker-compose -f docker-compose.prod.yml ps

# Logları kontrol et
docker-compose -f docker-compose.prod.yml logs -f
```

## 📞 İletişim
- **Acil Durumlar:** +90 xxx xxx xx xx
- **Email:** devops@finasis.com.tr
- **Slack:** #finasis-ops 