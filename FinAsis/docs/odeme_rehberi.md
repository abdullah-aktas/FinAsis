# Ödeme Rehberi (PayTR + Havale)

Bu doküman; PayTR entegrasyonu (checkout ve callback doğrulama) ile Havale/EFT akışını uçtan uca anlatır. Başlangıç için sandbox değerleri ile ilerleyin.

## 1) PayTR Kurulum
- Sandbox hesap oluşturun ve anahtarları alın:
  - `PAYTR_MERCHANT_ID`
  - `PAYTR_MERCHANT_KEY`
  - `PAYTR_MERCHANT_SALT`
- Django ayarları (`src/config/settings.py` veya .env):
  - `PAYTR_SANDBOX=True`
  - `PAYTR_ALLOWED_IPS` içine PayTR sandbox IP’lerini ekleyin (virgülle).

## 2) Checkout Başlatma
- Kullanıcı paket/plan seçer, `Transaction` oluşturulur.
- PayTR token/iframe talebi gönderilir ve kullanıcı ödeme sayfasına yönlendirilir.
- Başarılı/başarısız dönüş sonrası kullanıcı portal sayfasına döner.

## 3) Callback Doğrulama (Sunucu-sunucu)
- View: `src/apps/billing/views.py` içindeki `paytr_callback`.
- Doğrulamalar:
  - IP allowlist: `request.META["REMOTE_ADDR"]` PayTR IP’leri içinde olmalı.
  - HMAC-SHA256 + Base64 imza: `merchant_oid`, `status`, `total_amount` vb. alanlarla hesaplanır.
  - Idempotency: Aynı `merchant_oid` tekrar gelirse işlem durumu iki kez güncellenmez.
- Başarılı olduğunda:
  - İşlem `paid` yapılır, abonelik aktive edilir (plan/grup atamaları), fatura üretilir.
- Başarısız/şüpheli olduğunda:
  - Loglanır, 400 veya 403 döndürülür.

## 4) Havale/EFT Akışı
- Kullanıcı havale bildirir (banka adı, IBAN, tutar, açıklama/ref). `Transaction` veya ayrı kayıt oluşturulur.
- Staff panelinden manuel onay:
  - Yalnızca `is_staff` kullanıcılar.
  - Onay sonrası aynı aktivasyon ve fatura üretimi yapılır.
- Ayarlar (`settings.py`): `BANK_ACCOUNT_*` (Banka adı, IBAN, Alıcı adı), `BANK_TRANSFER_ENABLED=True`.

## 5) Fatura Oluşturma
- Başarılı aktivasyonda `Invoice` kaydı oluşturulur (fatura no/tarih, tutar, müşteri/şirket bilgisi).
- PDF/HTML çıktı (opsiyonel) kullanıcının portalında listelenebilir.

## 6) Test Senaryoları
- PayTR sandbox ile küçük bir tutar için ödeme başlatın, callback’in doğrulandığını ve aboneliğin aktifleştirildiğini kontrol edin.
- Hatalı imza/IP ile istek atarak reddedildiğini test edin.
- Havale bildirimi yapın, staff ile onaylayıp aboneliğin aktif olduğunu ve faturanın üretildiğini doğrulayın.

## 7) Sorun Giderme
- `TemplateDoesNotExist` (ödeme sayfaları/portal): İlgili template yolunu kontrol edin.
- `403` Callback: IP listesi eksik veya imza hatalı; `PAYTR_ALLOWED_IPS` ve anahtarlarınızı gözden geçirin.
- İki kez aktivasyon: Idempotent kontrolü ekli (aynı `merchant_oid` için tekrar aktivasyon yapılmaz).
- Loglarda hata yok mu?: `finasis.log` dosyasını inceleyin.

## 8) Canlıya Geçiş Notları
- `PAYTR_SANDBOX=False`, canlı anahtarlar ve IP listesi.
- `DEBUG=False`, güvenlik başlıkları ve HTTPS.
- Webhook/Callback URL’leri; güvenli ağ arkasında 200 döndüğünden emin olun.
