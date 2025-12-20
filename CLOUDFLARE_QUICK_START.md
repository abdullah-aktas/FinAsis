# ☁️ Cloudflare Hızlı Başlangıç

Bu rehber, Cloudflare'i Hetzner sunucusu ile entegre etmek için hızlı adımları içerir.

## ⚡ 5 Dakikada Cloudflare Kurulumu

### 1. Cloudflare Hesabı ve Domain Ekleme

1. [Cloudflare](https://dash.cloudflare.com/sign-up) hesabı oluşturun
2. "Add a Site" → `finasis.com.tr` ekleyin
3. **Free Plan** seçin
4. DNS kayıtlarını kontrol edin

### 2. DNS Yapılandırması

Cloudflare Dashboard → DNS → Records:

```
A Record:
  Name: finasis.com.tr
  IPv4: <hetzner-sunucu-ip>
  Proxy: ☁️ Proxied
  TTL: Auto

A Record:
  Name: www
  IPv4: <hetzner-sunucu-ip>
  Proxy: ☁️ Proxied
  TTL: Auto
```

**Önemli**: Proxy durumu **Proxied (☁️)** olmalı!

### 3. Nameserver Güncelleme

Domain sağlayıcınızda (Namecheap, GoDaddy, vb.) nameserver'ları Cloudflare'inkilerle değiştirin:

Cloudflare Dashboard → Overview → Nameservers bölümünden kopyalayın.

**Not**: Değişiklik 24-48 saat sürebilir.

### 4. SSL/TLS Ayarları

Cloudflare Dashboard → SSL/TLS:

1. **SSL/TLS encryption mode**: "Full (strict)"
2. **Always Use HTTPS**: Açık
3. **Minimum TLS Version**: TLS 1.2

### 5. Origin Certificate Oluşturma (Önerilir)

Cloudflare Dashboard → SSL/TLS → Origin Server:

1. "Create Certificate" → RSA (2048)
2. Hostnames: `finasis.com.tr`, `www.finasis.com.tr`
3. Certificate ve Private Key'i kopyalayın

Sunucuya yükleyin:

```bash
mkdir -p /etc/ssl/cloudflare
nano /etc/ssl/cloudflare/origin.crt  # Certificate'i yapıştırın
nano /etc/ssl/cloudflare/origin.key  # Private key'i yapıştırın
chmod 600 /etc/ssl/cloudflare/origin.key
chmod 644 /etc/ssl/cloudflare/origin.crt
```

### 6. Cloudflare IP Listesini Güncelleme

```bash
bash /opt/finasis/scripts/setup-cloudflare-ips.sh
```

### 7. Nginx Yapılandırması

```bash
# Cloudflare için özel config
cp /opt/finasis/deploy/nginx/finasis.com.tr.cloudflare.conf /etc/nginx/sites-available/finasis.com.tr

# Aktif et
ln -s /etc/nginx/sites-available/finasis.com.tr /etc/nginx/sites-enabled/

# Test et
nginx -t

# Yeniden başlat
systemctl reload nginx
```

### 8. Test

```bash
# Cloudflare üzerinden erişim testi
curl -I https://finasis.com.tr

# Response'da CF-Ray header'ı görünmeli
```

## ✅ Kontrol Listesi

- [ ] Cloudflare hesabı oluşturuldu
- [ ] Domain Cloudflare'e eklendi
- [ ] DNS kayıtları yapılandırıldı (Proxy: ☁️)
- [ ] Nameserver'lar güncellendi
- [ ] SSL/TLS mode: Full (strict)
- [ ] Origin Certificate oluşturuldu ve yüklendi
- [ ] Cloudflare IP listesi güncellendi
- [ ] Nginx Cloudflare config'i kullanılıyor
- [ ] Site çalışıyor: https://finasis.com.tr

## 🔧 Otomatik IP Güncelleme

Haftalık otomatik güncelleme için:

```bash
# Cron job ekle
echo "0 2 * * 0 root /opt/finasis/scripts/setup-cloudflare-ips.sh" >> /etc/crontab
```

## 📊 Cloudflare Page Rules (Önerilen)

Cloudflare Dashboard → Rules → Page Rules:

**Static Dosyalar:**

```
URL: finasis.com.tr/static/*
Cache Level: Cache Everything
Edge Cache TTL: 1 month
```

**Media Dosyalar:**

```
URL: finasis.com.tr/media/*
Cache Level: Cache Everything
Edge Cache TTL: 1 week
```

**API (Cache Yapma):**

```
URL: finasis.com.tr/api/*
Cache Level: Bypass
```

**Admin (Cache Yapma):**

```
URL: finasis.com.tr/admin/*
Cache Level: Bypass
```

## 🔍 Sorun Giderme

### 502/520/521 Hataları

- Origin sunucunun çalıştığını kontrol edin
- SSL sertifikasını kontrol edin
- Firewall kurallarını kontrol edin

### Gerçek IP Görünmüyor

```bash
# Cloudflare IP listesini kontrol edin
cat /etc/nginx/cloudflare-ips-v4.conf

# Nginx loglarını kontrol edin
tail -f /var/log/nginx/access.log
```

### Cache Sorunları

Cloudflare Dashboard → Caching → Purge Everything

## 💰 Maliyet

- **Cloudflare Free**: Ücretsiz
  - Unlimited bandwidth
  - DDoS koruması
  - SSL/TLS
  - CDN
  - Basic analytics

## 📚 Detaylı Rehber

Daha detaylı bilgi için: [CLOUDFLARE_DEPLOYMENT_GUIDE.md](CLOUDFLARE_DEPLOYMENT_GUIDE.md)
