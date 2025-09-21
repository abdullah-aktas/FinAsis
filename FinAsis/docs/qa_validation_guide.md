# FinAsis QA Doğrulama Rehberi

Bu rehber; FinAsis projesinin kurulumdan canlıya kadar fonksiyonel doğrulamalarını, güvenlik ve uyumluluk kontrollerini, rol bazlı kullanıcı senaryolarını ve otomasyon adımlarını içerir. Amaç; “her bir kullanıcı için işlevler tam çalışıyor mu?” sorusuna ölçülebilir ve tekrarlanabilir bir süreçle yanıt vermektir.

## 1) Ortam ve Kurulum
- Gereksinimler: Python 3.11+ (3.13 destekli), SQLite/PG, Node (frontend için), PowerShell.
- Sanal ortam:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```
- Django ayarları: `DJANGO_SETTINGS_MODULE=src.config.settings`
- Veritabanı ve statik dosyalar:
  ```powershell
  python manage.py migrate
  python manage.py collectstatic --noinput
  python manage.py createsuperuser
  ```
- Geliştirme sunucusu:
  ```powershell
  python manage.py runserver
  ```
- PayTR Sandbox env (gerekli):
  - `PAYTR_MERCHANT_ID`, `PAYTR_MERCHANT_KEY`, `PAYTR_MERCHANT_SALT`
  - `PAYTR_ALLOWED_IPS` (sandbox IP listesi) ve `PAYTR_SANDBOX=True`
- Banka/Havale bilgileri: `BANK_ACCOUNT_*` ayarları.

## 2) Rol ve Erişim Matrisi
- Anonim: Yalnızca halka açık sayfalar (ana sayfa, pricing, blog…); rapor endpoint’leri kapalı.
- Kullanıcı: Giriş yapmış standart kullanıcı; kendi şirket(ler)i üzerinden finans modülleri ve raporlar.
- Personel/Staff: Yönetim paneli ve bankadan havale onay akışlarına erişim.
- Süperuser: Tüm yönetim ve bakım görevleri.

Kontrol: `/yonetim/` ve banka havale onayı sadece staff/superuser; rapor sayfaları `login_required` ile korunur.

## 3) Duman (Smoke) Testleri
- Ana sayfa (`/`) yüklenir, header linkleri çalışır, CTA’lar yönlendirir.
- Kayıt/Giriş: `/accounts/register/` → benzersiz şirket verisi, `/accounts/login/` → başarılı giriş.
- Pricing (`/pricing/`) ve Contact (`/contact/`) açılır.
- Statikler: CSS/JS 200 döner, 404/500 özel şablonları mevcut.

## 4) Hesap/Üyelik Akışı
- Kayıt formu: Aynı vergi no ile mükerrer şirket oluşturulmaz (mevcut şirkete bağlanır).
- Giriş sonrası profil sayfası ve navbar’da kullanıcı durumu.
- Şifre sıfırlama e-postası (konsol backend) loglarda görüntülenir.

Doğrulama: Hatalı verilerde uygun form hataları; başarılı akışta redirect ve mesajlar.

## 5) Abonelik ve Ödeme
- Planlar ve Modüller: Plan → Modül → Grup atamaları doğru; aktivasyonda kullanıcı grup/izinleri güncellenir.
- PayTR (Sandbox):
  - Checkout başlatma → PayTR sayfası → başarılı ödeme → callback doğrulama (HMAC + IP allowlist) → Transaction güncel → abonelik aktive → fatura oluşturulur.
  - Başarısız/sahte callback: HMAC veya IP uymadığında reddedilir (loglanır, status değişmez).
- Havale/EFT:
  - Kullanıcı havale bildirimi oluşturur → staff panelden onay → abonelik aktive → fatura oluşturulur.
- Portal: Kullanıcı geçmiş işlemleri ve abonelik durumunu görür.

Test komutları (otomasyon yoksa manuel):
```powershell
# Testleri çalıştır (varsa):
pytest -q
```
Not: İlk kurulumlarda test keşfi için proje kökünden çalıştırın. Hata alırsanız bildiriniz.

## 6) Finans ve Raporlama
- Giriş gerekli: `yevmiye/kebir/mizan/envanter/kasa/demirbaş`, bilanço, gelir tablosu, nakit akışı, yaşlandırma, varyans ve beyanname ekranları.
- Şirket seçimi: `company` querystring parametresi ile filtre; yoksa `created_by` ilk şirket seçilir.
- Dönem seçimi: `year`, `month` veya `period` parametreleri.
- Dışa aktarma: `?excel=1` ve `?pdf=1` uçları dosya indirir.
- XML çıktıları: KDV/Muhtasar/BABS XML indirme.

Şablonlar: `templates/accounting/*.html` mevcut olmalı. Eksik şablonda 500/TemplateDoesNotExist alınır; bu durumda ilgili şablonu ekleyin (örn. `accounting/bilanco.html`).

## 7) Yönetim ve Yetki
- `/yonetim/` altı sadece staff; yardım/API uçları korunur.
- Banka havale onayı sadece staff; kötüye kullanıma karşı CSRF ve login zorunlu.
- Abonelik gerektiren ekranlar için (opsiyonel) `subscription_required` dekoratörü uygulanabilir.

## 8) Güvenlik Kontrol Listesi
- PayTR callback: HMAC-SHA256 + Base64, IP allowlist kontrolü, idempotent işlem güncelleme.
- Kimlik: `AUTH_USER_MODEL` kullanımı, session ayarları, `LOGIN_URL` set edilmiş.
- CSRF: Formlar ve POST uçları korunuyor.
- Yetki: Admin/management uçlarında `staff_required`; raporlarda `login_required`.
- Üretim: `DEBUG=False`, güvenli cookie, HSTS, `ALLOWED_HOSTS`, proxy arkası `SECURE_PROXY_SSL_HEADER` gerekirse.

## 9) Performans ve Stabilite
- N+1 sorgu kontrolleri (rapor queryleri gözden geçirin), gerekirse select_related/prefetch.
- Basit yük testi: kritik rapor sayfaları 200 ms altı hedef.
- Cache: Dosya cache aktif; rapor listelerinde uygun kullanın.

## 10) Gözlemlenebilirlik ve Loglama
- `finasis.log` dökümleri: ödeme callback, havale onayı, rapor hataları.
- Hata sayfaları 404/500 şablonları; ciddi hatalarda uyarı.
- Sürüm bilgisi ve değişiklikler için README/DOCS güncel.

## 11) Erişilebilirlik ve SEO
- A11y: Başlık hiyerarşisi, kontrast, odak, ARIA (header’da aktif link `aria-current`).
- SEO: `title`, `meta_description`, `meta_keywords`, `robots.txt` ve `sitemap.xml` kontrolü.

## 12) CI/CD ve Yayın
- Testler: `pytest -q` en azından çekirdek akışları geçmeli (auth, API sağlık, formlar, ikonlar, crawl, a11y, LMS API).
- Görev adımları (örnek):
  - Lint/format → test → migrate → collectstatic → deploy.

## 13) Sık Karşılaşılan Sorunlar
- TemplateDoesNotExist (ör. `accounting/bilanco.html`): İlgili şablonu `FinAsis/templates/accounting/` altında oluşturun ve veri bağlayın: `df`, `company`, `companies`, `year`, `month`.
- Anonim kullanıcı hatası (TypeError): İlgili rapor görünümleri `@login_required` ile korunmalı (uygulandı).
- PayTR callback doğrulama: IP listesi boşsa callback reddedilir; sandbox IP’lerini ayarlayın.

## 14) Kabul Kriterleri (Özet)
- [ ] Giriş/Çıkış/Kayıt kusursuz.
- [ ] Abonelik aktivasyonu hem PayTR hem Havale ile çalışır; fatura oluşur.
- [ ] Rapor sayfaları giriş sonrası açılır; Excel/PDF/XML dışa aktarma çalışır.
- [ ] Yönetim sayfaları yalnızca staff erişebilir.
- [ ] A11y/SEO temel kontrolleri sağlanır.
- [ ] Loglar temiz; kritik hatalar yok.

---
İsteğe bağlı: Bu rehbere göre eksik şablonları ve otomatik smoke testlerini (pytest) ekleyebilirim. Haber verin, uygulayayım.
