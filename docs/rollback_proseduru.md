# FinAsis Rollback ProsedÃ¼rÃ¼

## ğŸ”„ HÄ±zlÄ± Geri DÃ¶nÃ¼ÅŸ AdÄ±mlarÄ±

### 1. Rollback KararÄ±
AÅŸaÄŸÄ±daki durumlardan herhangi biri gerÃ§ekleÅŸtiÄŸinde rollback yapÄ±lmalÄ±dÄ±r:

- [ ] Kritik bir gÃ¼venlik aÃ§Ä±ÄŸÄ± tespit edildiÄŸinde
- [ ] Sistem performansÄ± kabul edilemez seviyeye dÃ¼ÅŸtÃ¼ÄŸÃ¼nde (response time > 2s)
- [ ] KullanÄ±cÄ± giriÅŸleri Ã§alÄ±ÅŸmadÄ±ÄŸÄ±nda
- [ ] E-Fatura entegrasyonu hata verdiÄŸinde
- [ ] VeritabanÄ± baÄŸlantÄ±sÄ± kesildiÄŸinde
- [ ] SSL sertifikasÄ± sorunlarÄ± oluÅŸtuÄŸunda

### 2. Rollback Ã–ncesi HazÄ±rlÄ±k
```bash
# Mevcut durumun yedeÄŸini al
./scripts/backup.sh

# Sistemin durumunu kontrol et
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### 3. Rollback Ä°ÅŸlemi
```bash
# Rollback script'ini Ã§alÄ±ÅŸtÄ±r
./scripts/rollback.sh YYYYMMDD_HHMMSS $SLACK_WEBHOOK_URL

# Servislerin durumunu kontrol et
docker-compose -f docker-compose.prod.yml ps
```

### 4. Rollback SonrasÄ± Kontroller

#### 4.1 Sistem Kontrolleri
- [ ] TÃ¼m servisler Ã§alÄ±ÅŸÄ±yor mu?
- [ ] VeritabanÄ± baÄŸlantÄ±sÄ± saÄŸlÄ±klÄ± mÄ±?
- [ ] Redis baÄŸlantÄ±sÄ± aktif mi?
- [ ] Celery worker'lar Ã§alÄ±ÅŸÄ±yor mu?

#### 4.2 Uygulama Kontrolleri
- [ ] API endpoint'leri Ã§alÄ±ÅŸÄ±yor mu?
- [ ] KullanÄ±cÄ± giriÅŸi yapÄ±labiliyor mu?
- [ ] E-Fatura oluÅŸturulabiliyor mu?
- [ ] PDF oluÅŸturma Ã§alÄ±ÅŸÄ±yor mu?
- [ ] Email gÃ¶nderimi aktif mi?

#### 4.3 Veri Kontrolleri
- [ ] VeritabanÄ± tutarlÄ± mÄ±?
- [ ] KullanÄ±cÄ± verileri korunmuÅŸ mu?
- [ ] Dosya yÃ¼klemeleri eriÅŸilebilir mi?
- [ ] Cache temizlendi mi?

### 5. Monitoring & Logging
```bash
# Prometheus metriklerini kontrol et
curl -f http://localhost:9090/api/v1/query?query=up

# Grafana dashboardlarÄ±nÄ± kontrol et
# http://grafana.finasis.com.tr

# Log dosyalarÄ±nÄ± incele
tail -f /var/log/finasis/django.log
tail -f /var/log/nginx/error.log
```

### 6. Ä°letiÅŸim & Raporlama

#### 6.1 Ä°Ã§ Ä°letiÅŸim
- [ ] DevOps ekibini bilgilendir
- [ ] YÃ¶netimi bilgilendir
- [ ] GeliÅŸtirme ekibini bilgilendir

#### 6.2 DÄ±ÅŸ Ä°letiÅŸim
- [ ] KullanÄ±cÄ±lara bilgilendirme emaili gÃ¶nder
- [ ] Status page'i gÃ¼ncelle
- [ ] MÃ¼ÅŸteri hizmetlerini bilgilendir

#### 6.3 DokÃ¼mantasyon
- [ ] Rollback nedenini kaydet
- [ ] YapÄ±lan iÅŸlemleri dokÃ¼mante et
- [ ] Ã–ÄŸrenilen dersleri kaydet
- [ ] Ä°yileÅŸtirme Ã¶nerilerini listele

### 7. Sonraki AdÄ±mlar
1. Root cause analysis yap
2. Benzer sorunlarÄ± Ã¶nlemek iÃ§in Ã¶nlemler al
3. Monitoring sistemini gÃ¼Ã§lendir
4. Test coverage'Ä± artÄ±r
5. Deployment sÃ¼recini gÃ¶zden geÃ§ir

## ğŸš¨ Acil Durum Ä°letiÅŸim Bilgileri

### DevOps Ekibi
- **NÃ¶betÃ§i DevOps:** +90 xxx xxx xx xx
- **DevOps Lead:** +90 xxx xxx xx xx
- **Slack:** #finasis-ops-911

### Sistem YÃ¶neticileri
- **Sistem YÃ¶neticisi:** +90 xxx xxx xx xx
- **Yedek Sistem YÃ¶neticisi:** +90 xxx xxx xx xx
- **Email:** sysadmin@finasis.com.tr

### Ãœst YÃ¶netim
- **CTO:** +90 xxx xxx xx xx
- **CEO:** +90 xxx xxx xx xx
- **Email:** management@finasis.com.tr 