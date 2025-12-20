# ☁️ Cloudflare Entegrasyonu

FinAsis projesi Cloudflare CDN ve DDoS koruması ile tam uyumludur.

## 📚 Dokümantasyon

- **[CLOUDFLARE_QUICK_START.md](CLOUDFLARE_QUICK_START.md)** - Hızlı başlangıç rehberi (5 dakika)
- **[CLOUDFLARE_DEPLOYMENT_GUIDE.md](CLOUDFLARE_DEPLOYMENT_GUIDE.md)** - Detaylı deployment rehberi

## 🚀 Hızlı Kurulum

1. **Cloudflare Hesabı**: [cloudflare.com](https://dash.cloudflare.com/sign-up) → Domain ekle
2. **DNS**: Proxy durumunu ☁️ Proxied yapın
3. **SSL/TLS**: Mode: Full (strict)
4. **Origin Certificate**: Oluşturup sunucuya yükleyin
5. **Nginx**: Cloudflare config'i kullanın
6. **IP Listesi**: Otomatik güncelleme scriptini çalıştırın

## 📁 Dosyalar

### Deployment
- `deploy/nginx/finasis.com.tr.cloudflare.conf` - Cloudflare için Nginx config
- `scripts/setup-cloudflare-ips.sh` - Cloudflare IP listesi güncelleme
- `scripts/deploy-with-cloudflare.sh` - Cloudflare ile deployment

### Kod
- `common/middleware/cloudflare.py` - Cloudflare middleware (gerçek IP desteği)
- `config/settings/base.py` - Middleware ayarları

## 🔧 Özellikler

✅ Gerçek kullanıcı IP'si desteği (CF-Connecting-IP)  
✅ Cloudflare ülke bilgisi (CF-IPCountry)  
✅ Cloudflare request ID (CF-Ray)  
✅ Nginx otomatik IP güncelleme  
✅ Origin Certificate desteği  
✅ Cache yönetimi (Page Rules)  

## 📝 Environment Variables

```env
USE_CLOUDFLARE=False  # Cloudflare kullanılıyorsa True
CLOUDFLARE_IP_HEADER=CF-Connecting-IP
```

## 🧪 Test

```bash
# Cloudflare üzerinden erişim
curl -I https://finasis.com.tr

# Response'da CF-Ray header'ı görünmeli
```

## 💡 Kullanım

Django view'larında:

```python
from common.middleware.cloudflare import get_real_ip, get_cloudflare_country

def my_view(request):
    real_ip = get_real_ip(request)
    country = get_cloudflare_country(request)
    # ...
```

## 🆘 Sorun Giderme

Detaylı sorun giderme için: [CLOUDFLARE_DEPLOYMENT_GUIDE.md](CLOUDFLARE_DEPLOYMENT_GUIDE.md#sorun-giderme)

