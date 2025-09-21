# Demo Senaryosu (Hızlı Sunum Akışı)

Bu runbook, 10-15 dakikalık bir ürün demosu için adım adım akışı içerir.

## Zaman Planı (öneri)
- 1 dk: Açılış ve değer önerisi
- 2 dk: Kayıt/Giriş
- 3 dk: Fiyatlandırma → PayTR ödeme (sandbox)
- 3 dk: Abonelik aktivasyonu → Fatura gösterimi
- 3 dk: Finans raporları + AI/Otomasyon vurgusu
- 2 dk: Güvenlik/uyum ve kapanış

## Hazırlık
- Sandbox PayTR anahtarları ve IP listesi ayarlı.
- Bir test kullanıcısı ve en az 1 şirket kaydı mevcut.
- Örnek veri: birkaç fatura/gelir-gider kaydı (opsiyonel).

Hızlı komutlar (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Faydalı URL’ler:
- Ana sayfa: http://127.0.0.1:8000/
- Kayıt: http://127.0.0.1:8000/accounts/register/
- Giriş: http://127.0.0.1:8000/accounts/login/
- Fiyatlandırma: http://127.0.0.1:8000/pricing/
- Bilanço: http://127.0.0.1:8000/accounting/finansal/bilanco/
- Gelir Tablosu: http://127.0.0.1:8000/accounting/finansal/gelir-tablosu/
- Nakit Akışı: http://127.0.0.1:8000/accounting/finansal/nakit-akisi/
- AI Otomasyon Önizleme: http://127.0.0.1:8000/accounting/auto-book/

## Adımlar
1) Açılış ve Değer Önerisi
- Ana sayfa: Yerel AI, e‑Dönüşüm, Blockchain ve sosyal kanıt bölümlerini gösterin.
- CTA’lar ve header navigasyonu.

2) Kayıt/Giriş
- Yeni kullanıcı oluşturun veya test kullanıcısı ile giriş yapın.

3) Fiyatlandırma ve Plan Seçimi
- `/pricing/` üzerinden plan kartlarını gösterin; plan seçerek ödeme akışını başlatın.

4) PayTR Ödeme
- Checkout ekranını gösterin (sandbox), başarılı ödeme yapın.
- Callback sonrası abonelik durumunun “aktif” olduğunu ve faturanın oluştuğunu portalda gösterin.

5) Havale Akışı (Alternatif)
- Kullanıcı olarak havale bildirimi oluşturun.
- Staff hesabıyla yönetimden bildirimi onaylayın; abonelik ve faturayı kontrol edin.

6) Finans Modülü ve Raporlar
- Bilanço/Gelir Tablosu/Nakit Akışı sayfalarını açın.
- Excel/PDF dışa aktarma butonlarını gösterin.

7) AI/Otomasyon Vurgusu
- `accounting/auto-book/` önizleme ekranını açın (login gerekli); OCR/kurallar ile otomasyon mesajını verin.

8) Güvenlik ve Uyum
- HMAC/IP doğrulamalı callback, admin yetkileri, login korumaları.

### Alternatif/Fallback Akışları
- PayTR erişimi yoksa: Havale bildirimi oluşturun, staff hesabı ile onaylayın; aboneliğin aktifleştirilmesini ve faturayı gösterin.
- Örnek veri yoksa: Rapor sayfalarında filtre formunu (şirket/yıl/ay) gösterin, dışa aktarma butonlarını tanıtın; demo amaçlı veri olmadığını belirtin.

### Sorun Giderme (Demo sırasında)
- Girişe yönlendiriyorsa: Önce login olun; rapor sayfaları `login_required`.
- Template bulunamadı: `templates/accounting/` altında ilgili şablon mevcut mu bakın.
- PayTR callback 403: Sandbox IP/anahtarlar eksik olabilir; ödeme rehberine bakın (`docs/odeme_rehberi.md`).
- Yavaşlık: Konsolda uyarı/hata var mı? Gerekirse yalnızca akışları sözlü anlatın.

## Kapanış
- SSS kısa yanıtlar; destek ve satış e-postaları (`support@`, `sales@`).
- Yol haritası: Kurumsal özellikler, entegrasyonlar, rapor zenginliği.

## Demo Kontrol Listesi
- [ ] PayTR sandbox anahtarları ve IP listesi ayarlı
- [ ] Test kullanıcısı ile giriş başarılı
- [ ] Plan seçimi → ödeme → abonelik aktif
- [ ] Fatura üretimi ve görünürlüğü
- [ ] Bilanço/Gelir/Nakit sayfaları açılıyor, export linkleri çalışıyor
- [ ] AI önizleme sayfası açılıyor (login)
- [ ] Havale fallback (gerekirse) çalışıyor
