# ☁️ Cloudflare ile FinAsis Deployment Rehberi

Bu rehber, finasis.com.tr'yi Hetzner sunucusunda Cloudflare CDN ve DDoS koruması ile nasıl yayınlayacağınızı açıklar.

## 🎯 Cloudflare'in Avantajları

- **CDN**: Statik içerik dünya çapında hızlı dağıtım
- **DDoS Koruması**: Otomatik saldırı koruması
- **SSL/TLS**: Ücretsiz ve otomatik SSL sertifikaları
- **Caching**: Gelişmiş önbellekleme seçenekleri
- **Analytics**: Detaylı trafik analizi
- **Firewall Rules**: Gelişmiş güvenlik kuralları
- **Page Rules**: URL bazlı özelleştirmeler

## 📋 Ön Gereksinimler

1. Hetzner sunucusu kurulu ve çalışıyor olmalı
2. Domain (finasis.com.tr) sahibi olmalısınız
3. Cloudflare hesabı oluşturulmalı (ücretsiz)

## 🚀 Adım 1: Cloudflare Hesabı ve Domain Ekleme

### 1.1 Cloudflare Hesabı Oluşturma

1. [Cloudflare](https://dash.cloudflare.com/sign-up) hesabı oluşturun
2. "Add a Site" butonuna tıklayın
3. Domain'inizi girin: `finasis.com.tr`
4. Plan seçin: **Free** (başlangıç için yeterli)

### 1.2 DNS Kayıtlarını Kontrol Etme

Cloudflare otomatik olarak DNS kayıtlarınızı tarar. Şunları kontrol edin:

- **A Record**: `finasis.com.tr` → Hetzner sunucu IP'si
- **A Record**: `www.finasis.com.tr` → Hetzner sunucu IP'si
- **CNAME**: Diğer subdomain'ler (varsa)

**Önemli**: Cloudflare proxy aktif olmalı (turuncu bulut ikonu ☁️)

## 🔧 Adım 2: Cloudflare DNS Yapılandırması

### 2.1 DNS Kayıtları

Cloudflare Dashboard → DNS → Records:

```
Type: A
Name: finasis.com.tr
IPv4 address: <hetzner-sunucu-ip>
Proxy status: Proxied (☁️)
TTL: Auto

Type: A
Name: www
IPv4 address: <hetzner-sunucu-ip>
Proxy status: Proxied (☁️)
TTL: Auto
```

### 2.2 Nameserver'ları Güncelleme

Domain sağlayıcınızda (Namecheap, GoDaddy, vb.) nameserver'ları Cloudflare'inkilerle değiştirin:

Cloudflare Dashboard → Overview → Nameservers bölümünden nameserver'ları kopyalayın:

```
Örnek:
ns1.cloudflare.com
ns2.cloudflare.com
```

**Not**: Nameserver değişikliği 24-48 saat sürebilir.

## 🔒 Adım 3: Cloudflare SSL/TLS Yapılandırması

### 3.1 SSL/TLS Ayarları

Cloudflare Dashboard → SSL/TLS → Overview:

1. **SSL/TLS encryption mode**: "Full (strict)" seçin

   - Bu, Cloudflare ile origin sunucu arasında şifreli bağlantı sağlar
   - Origin sunucuda geçerli bir SSL sertifikası olmalı

2. **Always Use HTTPS**: Açık

   - HTTP istekleri otomatik olarak HTTPS'e yönlendirilir

3. **Minimum TLS Version**: TLS 1.2
   - Modern ve güvenli

### 3.2 Origin Certificate (Opsiyonel - Önerilir)

Cloudflare Dashboard → SSL/TLS → Origin Server:

1. "Create Certificate" butonuna tıklayın
2. Private key type: RSA (2048)
3. Hostnames: `finasis.com.tr`, `www.finasis.com.tr`
4. Certificate validity: 15 years
5. "Create" butonuna tıklayın
6. Certificate ve Private Key'i kopyalayın

**Origin Certificate'i sunucuya yükleme:**

```bash
# Certificate dizini oluştur
mkdir -p /etc/ssl/cloudflare

# Certificate'i kaydet
nano /etc/ssl/cloudflare/origin.crt
# (Cloudflare'den kopyaladığınız certificate'i yapıştırın)

# Private key'i kaydet
nano /etc/ssl/cloudflare/origin.key
# (Cloudflare'den kopyaladığınız private key'i yapıştırın)

# İzinleri ayarla
chmod 600 /etc/ssl/cloudflare/origin.key
chmod 644 /etc/ssl/cloudflare/origin.crt
```

## 🌐 Adım 4: Nginx Yapılandırması (Cloudflare için)

### 4.1 Cloudflare IP Listesi

Cloudflare'in IP adreslerini otomatik olarak güncellemek için script kullanın:

```bash
# Cloudflare IP listesini indir
curl -s https://www.cloudflare.com/ips-v4 > /etc/nginx/cloudflare-ips-v4.conf
curl -s https://www.cloudflare.com/ips-v6 > /etc/nginx/cloudflare-ips-v6.conf

# Nginx formatına dönüştür
sed -i 's/^/set_real_ip_from /' /etc/nginx/cloudflare-ips-v4.conf
sed -i 's/$/;/' /etc/nginx/cloudflare-ips-v4.conf
sed -i 's/^/set_real_ip_from /' /etc/nginx/cloudflare-ips-v6.conf
sed -i 's/$/;/' /etc/nginx/cloudflare-ips-v6.conf

# Real IP header'ı ekle
echo "real_ip_header CF-Connecting-IP;" >> /etc/nginx/cloudflare-ips-v4.conf
echo "real_ip_header CF-Connecting-IP;" >> /etc/nginx/cloudflare-ips-v6.conf
```

### 4.2 Nginx Config (Cloudflare için)

Cloudflare için özel Nginx yapılandırması kullanın:

```bash
cp /opt/finasis/deploy/nginx/finasis.com.tr.cloudflare.conf /etc/nginx/sites-available/finasis.com.tr
ln -s /etc/nginx/sites-available/finasis.com.tr /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

## ⚡ Adım 5: Cloudflare Caching Yapılandırması

### 5.1 Caching Ayarları

Cloudflare Dashboard → Caching → Configuration:

- **Caching Level**: Standard
- **Browser Cache TTL**: Respect Existing Headers
- **Always Online**: On
- **Auto Minify**: HTML, CSS, JavaScript (opsiyonel)

### 5.2 Page Rules (Önerilen)

Cloudflare Dashboard → Rules → Page Rules:

**Kural 1: Static Dosyalar**

```
URL Pattern: finasis.com.tr/static/*
Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 month
```

**Kural 2: Media Dosyalar**

```
URL Pattern: finasis.com.tr/media/*
Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 week
```

**Kural 3: API Endpoints (Cache Yapma)**

```
URL Pattern: finasis.com.tr/api/*
Settings:
  - Cache Level: Bypass
```

**Kural 4: Admin Panel (Cache Yapma)**

```
URL Pattern: finasis.com.tr/admin/*
Settings:
  - Cache Level: Bypass
```

## 🔥 Adım 6: Cloudflare Firewall Rules

### 6.1 Güvenlik Kuralları

Cloudflare Dashboard → Security → WAF:

**Önerilen Kurallar:**

1. **Rate Limiting** (Free plan'da sınırlı)

   - API endpoint'leri için rate limit ekleyin

2. **Security Level**: Medium

   - Otomatik tehdit koruması

3. **Challenge Passage**: 30 minutes
   - Bot koruması için

### 6.2 Firewall Rules (Opsiyonel - Pro plan)

```
Rule Name: Block Admin from Non-Turkey
Expression: (http.request.uri.path contains "/admin") and (ip.geoip.country ne "TR")
Action: Block
```

## 📊 Adım 7: Cloudflare Analytics ve Monitoring

### 7.1 Analytics

Cloudflare Dashboard → Analytics:

- **Web Analytics**: Trafik istatistikleri
- **Security Events**: Güvenlik olayları
- **Performance**: Performans metrikleri

### 7.2 Notifications

Cloudflare Dashboard → Notifications:

- DDoS saldırıları için email bildirimleri
- SSL sertifika yenileme uyarıları

## 🔄 Adım 8: Otomatik Cloudflare IP Güncelleme

### 8.1 Cron Job Oluşturma

```bash
nano /etc/cron.weekly/update-cloudflare-ips.sh
```

İçeriği:

```bash
#!/bin/bash
# Cloudflare IP listesini haftalık güncelle

curl -s https://www.cloudflare.com/ips-v4 > /etc/nginx/cloudflare-ips-v4.conf
curl -s https://www.cloudflare.com/ips-v6 > /etc/nginx/cloudflare-ips-v6.conf

sed -i 's/^/set_real_ip_from /' /etc/nginx/cloudflare-ips-v4.conf
sed -i 's/$/;/' /etc/nginx/cloudflare-ips-v4.conf
sed -i 's/^/set_real_ip_from /' /etc/nginx/cloudflare-ips-v6.conf
sed -i 's/$/;/' /etc/nginx/cloudflare-ips-v6.conf

echo "real_ip_header CF-Connecting-IP;" >> /etc/nginx/cloudflare-ips-v4.conf
echo "real_ip_header CF-Connecting-IP;" >> /etc/nginx/cloudflare-ips-v6.conf

systemctl reload nginx
```

Çalıştırılabilir yap:

```bash
chmod +x /etc/cron.weekly/update-cloudflare-ips.sh
```

## 🧪 Adım 9: Test ve Doğrulama

### 9.1 Cloudflare Proxy Kontrolü

```bash
# Cloudflare üzerinden erişim
curl -I https://finasis.com.tr

# Response header'larında CF-Ray görünmeli
# X-Forwarded-For header'ında gerçek IP görünmeli
```

### 9.2 SSL Test

[SSL Labs Test](https://www.ssllabs.com/ssltest/) ile SSL yapılandırmasını test edin.

### 9.3 Gerçek IP Kontrolü

Django'da gerçek IP'yi kontrol edin:

```python
# Django view'da
real_ip = request.META.get('HTTP_CF_CONNECTING_IP', request.META.get('REMOTE_ADDR'))
```

## 🔧 Sorun Giderme

### Cloudflare 502/520/521 Hataları

**502 Bad Gateway:**

- Origin sunucunun çalıştığını kontrol edin
- Nginx yapılandırmasını kontrol edin

**520 Web Server Returned an Unknown Error:**

- Origin sunucuda SSL hatası olabilir
- Origin certificate'i kontrol edin

**521 Web Server Is Down:**

- Origin sunucu kapalı veya erişilemiyor
- Firewall kurallarını kontrol edin

### Gerçek IP Görünmüyor

```bash
# Nginx loglarını kontrol edin
tail -f /var/log/nginx/access.log

# Cloudflare IP listesinin güncel olduğundan emin olun
cat /etc/nginx/cloudflare-ips-v4.conf
```

### Cache Sorunları

```bash
# Cloudflare cache'i temizle
# Cloudflare Dashboard → Caching → Purge Everything

# Veya belirli URL'leri temizle
# Cloudflare Dashboard → Caching → Custom Purge
```

## 📝 Önemli Notlar

1. **Cloudflare Proxy Aktif**: DNS kayıtlarında turuncu bulut (☁️) olmalı
2. **SSL Mode**: "Full (strict)" kullanın
3. **Origin Certificate**: Cloudflare ile origin arasında şifreli bağlantı için
4. **Real IP**: Nginx'te Cloudflare IP'lerini tanımlayın
5. **Cache Rules**: API ve admin panel'i cache'leme
6. **Rate Limiting**: API endpoint'leri için rate limit ekleyin

## 💰 Maliyet

- **Cloudflare Free Plan**: Ücretsiz

  - Unlimited bandwidth
  - DDoS koruması
  - SSL/TLS
  - CDN
  - Basic analytics

- **Cloudflare Pro Plan**: $20/ay (opsiyonel)
  - Advanced DDoS koruması
  - Image optimization
  - Advanced analytics
  - Page Rules (20 adet)

## 🎯 Önerilen Yapılandırma Özeti

```
Internet → Cloudflare CDN → Hetzner Sunucu
         (DDoS Koruması)   (Origin Server)
         (SSL/TLS)         (Django App)
         (Caching)         (PostgreSQL)
         (Analytics)       (Redis)
```

## 🆘 Yardım

Sorun yaşarsanız:

1. Cloudflare Dashboard → Analytics → Events
2. Nginx loglarını kontrol edin
3. Origin sunucu loglarını kontrol edin
4. Cloudflare Status sayfasını kontrol edin: https://www.cloudflarestatus.com/
