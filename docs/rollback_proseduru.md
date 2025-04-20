# FinAsis Rollback Prosedürü

## 🔄 Hızlı Geri Dönüş Adımları

### 1. Rollback Kararı
Aşağıdaki durumlardan herhangi biri gerçekleştiğinde rollback yapılmalıdır:

- [ ] Kritik bir güvenlik açığı tespit edildiğinde
- [ ] Sistem performansı kabul edilemez seviyeye düştüğünde (response time > 2s)
- [ ] Kullanıcı girişleri çalışmadığında
- [ ] E-Fatura entegrasyonu hata verdiğinde
- [ ] Veritabanı bağlantısı kesildiğinde
- [ ] SSL sertifikası sorunları oluştuğunda

### 2. Rollback Öncesi Hazırlık
```bash
# Mevcut durumun yedeğini al
./scripts/backup.sh

# Sistemin durumunu kontrol et
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### 3. Rollback İşlemi
```bash
# Rollback script'ini çalıştır
./scripts/rollback.sh YYYYMMDD_HHMMSS $SLACK_WEBHOOK_URL

# Servislerin durumunu kontrol et
docker-compose -f docker-compose.prod.yml ps
```

### 4. Rollback Sonrası Kontroller

#### 4.1 Sistem Kontrolleri
- [ ] Tüm servisler çalışıyor mu?
- [ ] Veritabanı bağlantısı sağlıklı mı?
- [ ] Redis bağlantısı aktif mi?
- [ ] Celery worker'lar çalışıyor mu?

#### 4.2 Uygulama Kontrolleri
- [ ] API endpoint'leri çalışıyor mu?
- [ ] Kullanıcı girişi yapılabiliyor mu?
- [ ] E-Fatura oluşturulabiliyor mu?
- [ ] PDF oluşturma çalışıyor mu?
- [ ] Email gönderimi aktif mi?

#### 4.3 Veri Kontrolleri
- [ ] Veritabanı tutarlı mı?
- [ ] Kullanıcı verileri korunmuş mu?
- [ ] Dosya yüklemeleri erişilebilir mi?
- [ ] Cache temizlendi mi?

### 5. Monitoring & Logging
```bash
# Prometheus metriklerini kontrol et
curl -f http://localhost:9090/api/v1/query?query=up

# Grafana dashboardlarını kontrol et
# http://grafana.finasis.com.tr

# Log dosyalarını incele
tail -f /var/log/finasis/django.log
tail -f /var/log/nginx/error.log
```

### 6. İletişim & Raporlama

#### 6.1 İç İletişim
- [ ] DevOps ekibini bilgilendir
- [ ] Yönetimi bilgilendir
- [ ] Geliştirme ekibini bilgilendir

#### 6.2 Dış İletişim
- [ ] Kullanıcılara bilgilendirme emaili gönder
- [ ] Status page'i güncelle
- [ ] Müşteri hizmetlerini bilgilendir

#### 6.3 Dokümantasyon
- [ ] Rollback nedenini kaydet
- [ ] Yapılan işlemleri dokümante et
- [ ] Öğrenilen dersleri kaydet
- [ ] İyileştirme önerilerini listele

### 7. Sonraki Adımlar
1. Root cause analysis yap
2. Benzer sorunları önlemek için önlemler al
3. Monitoring sistemini güçlendir
4. Test coverage'ı artır
5. Deployment sürecini gözden geçir

## 🚨 Acil Durum İletişim Bilgileri

### DevOps Ekibi
- **Nöbetçi DevOps:** +90 xxx xxx xx xx
- **DevOps Lead:** +90 xxx xxx xx xx
- **Slack:** #finasis-ops-911

### Sistem Yöneticileri
- **Sistem Yöneticisi:** +90 xxx xxx xx xx
- **Yedek Sistem Yöneticisi:** +90 xxx xxx xx xx
- **Email:** sysadmin@finasis.com.tr

### Üst Yönetim
- **CTO:** +90 xxx xxx xx xx
- **CEO:** +90 xxx xxx xx xx
- **Email:** management@finasis.com.tr 