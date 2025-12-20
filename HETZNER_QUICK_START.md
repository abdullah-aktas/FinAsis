# 🚀 Hetzner'da Hızlı Başlangıç

Bu rehber, finasis.com.tr'yi Hetzner'da en hızlı şekilde yayınlamanızı sağlar.

## ⚡ Hızlı Kurulum (5 Adım)

### 1. Hetzner Sunucu Oluştur

1. [Hetzner Cloud Console](https://console.hetzner.cloud/) → "Add Server"
2. **Önerilen**: CPX31 (4 vCPU, 8GB RAM) veya CPX41 (8 vCPU, 16GB RAM)
3. **Location**: Nuremberg
4. **Image**: Ubuntu 22.04
5. Sunucuyu oluştur ve IP adresini not et

### 2. Sunucuya Bağlan ve Kurulum Yap

```bash
# Sunucuya SSH ile bağlan
ssh root@<sunucu-ip-adresi>

# Kurulum scriptini çalıştır
curl -fsSL https://raw.githubusercontent.com/<repo>/scripts/setup-hetzner-server.sh | bash

# VEYA manuel olarak:
bash <(curl -fsSL https://raw.githubusercontent.com/<repo>/scripts/setup-hetzner-server.sh)
```

### 3. Projeyi Yükle

```bash
# Proje dizinine git
cd /opt/finasis

# Git ile klonla (önerilen)
git clone <repository-url> .

# VEYA SCP ile yükle (yerel bilgisayarınızdan)
# scp -r /path/to/FinAsis root@<sunucu-ip>:/opt/finasis/
```

### 4. Environment Dosyasını Oluştur

```bash
cd /opt/finasis
cp env.example .env
nano .env
```

**Önemli değişkenler:**
- `DJANGO_SECRET_KEY` - Güçlü bir secret key oluşturun
- `DJANGO_DB_PASSWORD` - Veritabanı şifresi
- `DJANGO_ALLOWED_HOSTS` - finasis.com.tr,www.finasis.com.tr

**Secret key oluşturma:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 5. Deploy Et

```bash
cd /opt/finasis
bash scripts/deploy-hetzner.sh
```

## 🌐 Domain ve SSL Kurulumu

### 1. DNS Ayarları

Domain sağlayıcınızda (ör. Namecheap, GoDaddy):

```
A Record: finasis.com.tr → <sunucu-ip>
A Record: www.finasis.com.tr → <sunucu-ip>
```

### 2. Nginx Yapılandırması

```bash
# Nginx config dosyasını kopyala
cp /opt/finasis/deploy/nginx/finasis.com.tr.conf /etc/nginx/sites-available/finasis.com.tr

# Aktif et
ln -s /etc/nginx/sites-available/finasis.com.tr /etc/nginx/sites-enabled/

# Test et
nginx -t

# Nginx'i yeniden başlat
systemctl reload nginx
```

### 3. SSL Sertifikası (Let's Encrypt)

```bash
certbot --nginx -d finasis.com.tr -d www.finasis.com.tr
```

Sertifika otomatik olarak yenilenecek.

## ✅ Kontrol Listesi

- [ ] Sunucu oluşturuldu
- [ ] Kurulum scripti çalıştırıldı
- [ ] Proje yüklendi
- [ ] .env dosyası oluşturuldu ve yapılandırıldı
- [ ] Deploy scripti çalıştırıldı
- [ ] DNS ayarları yapıldı
- [ ] Nginx yapılandırıldı
- [ ] SSL sertifikası alındı
- [ ] Site çalışıyor: https://finasis.com.tr

## 🔍 Sorun Giderme

### Container başlamıyor
```bash
cd /opt/finasis
docker compose -f docker-compose.hetzner.yml logs
```

### Veritabanı bağlantı hatası
```bash
docker compose -f docker-compose.hetzner.yml exec db psql -U finasis -d finasis
```

### Nginx 502 hatası
```bash
# Container'ın çalıştığını kontrol et
docker compose -f docker-compose.hetzner.yml ps

# Port kontrolü
netstat -tlnp | grep 8080
```

### Static dosyalar görünmüyor
```bash
docker compose -f docker-compose.hetzner.yml exec finasis python manage.py collectstatic --noinput
```

## 📊 Yönetim Komutları

### Logları görüntüle
```bash
docker compose -f docker-compose.hetzner.yml logs -f finasis
```

### Container'ları yeniden başlat
```bash
docker compose -f docker-compose.hetzner.yml restart
```

### Veritabanı yedeği al
```bash
docker compose -f docker-compose.hetzner.yml exec db pg_dump -U finasis finasis > backup_$(date +%Y%m%d).sql
```

### Yeni deployment
```bash
cd /opt/finasis
bash scripts/deploy-hetzner.sh
```

## 💰 Maliyet

- **Hetzner Cloud CPX31**: ~€15/ay (4 vCPU, 8GB RAM)
- **Hetzner Cloud CPX41**: ~€30/ay (8 vCPU, 16GB RAM)
- **Domain**: ~€10-15/yıl
- **SSL**: Ücretsiz (Let's Encrypt)

**Toplam**: ~€15-30/ay (Google Cloud'a göre çok daha ekonomik!)

## 📚 Detaylı Rehber

Daha detaylı bilgi için: [HETZNER_DEPLOYMENT_GUIDE.md](HETZNER_DEPLOYMENT_GUIDE.md)

## 🆘 Yardım

Sorun yaşarsanız:
1. Logları kontrol edin
2. Container durumunu kontrol edin
3. Nginx yapılandırmasını test edin
4. DNS ayarlarını doğrulayın

