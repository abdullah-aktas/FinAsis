# FinAsis Sistem Admin Kullanma Kılavuzu

Bu kılavuz, FinAsis platformunun sistem yöneticileri (Sistem Admin) için kapsamlı bir operasyon, güvenlik ve bakım rehberidir. Şirket adminleri (tek tenant odaklı) için de geçerlidir ancak yetki kapsamı daraltılmıştır.

---

## 1) Rol Tanımı ve Yetki Kapsamı

- Sistem Admin (Platform Seviyesi)
  - Tüm tenant/şirketlere erişim
  - Global ayarlar, lisans/plan, entegrasyonlar
  - Güvenlik politikaları, denetim ve olay yönetimi
- Şirket Admin (Tenant Seviyesi)
  - Kendi şirketinde kullanıcı, rol, abonelik, e-dönüşüm yönetimi

En az ayrıcalık prensibi: Yalnızca gerekli izinleri verin; periyodik olarak erişimleri gözden geçirin.

---

## 2) Mimari Genel Bakış

- Django (Backend) + REST API
- Modüller: accounts, accounting, finance, ai_assistant, billing, permissions, tenancy
- Çok şirketli yapı: `tenancy` ve şirket ilişkileri
- Ödeme: PayTR entegrasyonu (sandbox/production)
- E-dönüşüm: e-fatura/e-defter entegrasyonları
- AI: Risk skorlama, tahmin, OCR (opsiyonel bağımlılıklar)

---

## 3) İlk Kurulum ve Onboarding

1. Süper kullanıcı oluşturun:
   ```powershell
   python manage.py createsuperuser
   ```
2. Gerekli seed işlemleri:
   ```powershell
   python manage.py seed_roles
   python manage.py seed_billing_plans
   ```
3. PayTR sandbox anahtarlarını girin (bkz. `docs/odeme_rehberi.md`).
4. E-dönüşüm ayarlarını yapılandırın (e-fatura, e-defter).
5. İlk tenant/şirketi ve Şirket Admin kullanıcılarını oluşturun.
6. Rol/İzinleri doğrulayın; gereksiz ayrıcalıkları kaldırın.

---

## 4) Günlük Operasyonlar (Runbook)

- Kullanıcı taleplerini onaylayın, roller atayın.
- Başarısız girişler ve olağan dışı aktiviteler için logları kontrol edin.
- Ödeme/abonelik durumlarını takip edin; başarısız ödemeler için bildirim gönderin.
- Kritik uyarılar: Hatalı webhook, 403 callback, cron/kuyruk gecikmeleri.

### Haftalık Bakım
- Rapor üretim ve paylaşım yetkilerini gözden geçirin.
- AI/otomasyon kuyruklarını, job sonuçlarını ve sürelerini inceleyin.
- Yedekleme job’larının başarı raporlarını kontrol edin.

### Aylık Bakım
- Abonelik yenilemeleri ve faturalandırma özetleri.
- Rol/izin denetimi (least privilege)
- KVKK/GDPR gereği veri saklama/silme politikaları.

---

## 5) Kritik Yönetim Akışları

### 5.1 Kullanıcı Yönetimi
- Yeni kullanıcı oluşturma: `/accounts/users/`
- Role atama: Owner/Admin/Accountant/Viewer veya özel rol
- SSO/2FA politikası (varsa) uygula; parola politikası zorunluluğu

### 5.2 Tenant/Şirket Yönetimi
- Yeni tenant + şirket oluşturma
- `UserTenantRole` ile kullanıcıları tenant’a bağlama
- Konsolidasyon ve çok şirketli raporlar için erişim kontrolü

### 5.3 Abonelik ve Faturalama
- Plan atama/değiştirme (`/billing/`)
- PayTR callback loglarını izleme; başarısız ödemeler için yeniden deneme
- Havale bildirim onayı (alternatif akış)

### 5.4 Roller ve İzinler
- Hazır roller (Admin, Accountant, Auditor, InventoryManager)
- Özel rol oluşturma; modül bazlı izin (READ/CREATE/UPDATE/DELETE/APPROVE/EXPORT/REPORT/ADMIN)
- Yetki devri ve iz sürülebilirlik (audit trail)

### 5.5 Güvenlik ve Denetim
- MFA/2FA ve parola politikaları
- IP allowlist, HMAC imzalı webhook
- Denetim logları: fatura silme, rol değişimi, ödeme onayı gibi hassas işlemler

---

## 6) Olay Yönetimi (Incident Response)

1. Tespit: Log, alarm, kullanıcı şikayeti
2. Sınıflandırma: Kritik/Orta/Düşük etki
3. İzolasyon: İlgili servis veya kullanıcı erişimini geçici kısıtlama
4. Analiz: Loglar, son dağıtım, veri tutarlılığı
5. Çözüm: Konfig düzeltme, rollback, hotfix
6. İletişim: Paydaşlara durum bilgilendirmesi
7. Kapanış: Kök neden analizi (RCA), önleyici aksiyonlar

Playbook Örnekleri:
- PayTR Callback 403: IP/anahtar doğrula, log incele, tekrar dene
- E-fatura Gönderimi Hatası: Entegrasyon anahtarları ve servis durumu, yeniden gönderim
- Performans Sorunu: N+1 analiz, indeks/önbellek, sorgu optimizasyonu

---

## 7) Yedekleme ve Geri Yükleme (Backup/Restore)

- Günlük veritabanı yedeği + medya klasörü senkronizasyonu
- 30/90 gün saklama politikası (ihtiyaca göre)
- Şifreli yedek depolama (KMS/KeyVault)
- Periyodik geri yükleme testi (DR/BCP tatbikatı)

Adımlar (örnek, ortamınıza göre uyarlayın):
1. Veritabanı dump alın (otomatik job)
2. Medya dosyalarını object storage’a senkronize edin
3. Test ortamında restore edin ve smoke test çalıştırın

---

## 8) Performans ve Ölçeklenebilirlik

- N+1 önleme: `select_related`, `prefetch_related`
- Önbellekleme: Sık kullanılan listeler ve raporlar
- Asenkron işler: Kuyruk (RQ/Celery) kullanımı
- İzleme: APM/metrics (istek süresi, hata oranı, kuyruk süresi)

---

## 9) Uyumluluk ve Veri Gizliliği

- KVKK/GDPR veri sınıflandırma ve işleme kayıtları (`finance.data_security_compliance` modelleri)
- Erişim logları, rıza kayıtları, maskeleme/anonimleştirme
- Veri minimizasyonu ve saklama süreleri

---

## 10) Denetim ve Raporlama

- Yönetim raporları: Abonelik, gelir, aktif kullanıcı
- Güvenlik raporları: Yetki değişimleri, başarısız girişler
- Operasyon raporları: Job başarı/başarısızlık, entegrasyon sağlık kontrolleri

---

## 11) CLI ve Yönetim Komutları

```powershell
# Süper kullanıcı
python manage.py createsuperuser

# Roller ve planlar
python manage.py seed_roles
python manage.py seed_billing_plans

# Opsiyonel: demo senaryoları
python scripts/create_demo_scenarios.py --type all
```

---

## 12) Sorun Giderme Hızlı Rehber

- Giriş sorunu → Şifre sıfırla, hesap durumu kontrol
- Rapor boş → Filtre/şirket ve demo veri doğrula
- Ödeme 403 → IP/anahtar/callback URL
- E-fatura pasif → Plan/izin/modül lisansı
- Yavaşlık → N+1, indeks, cache, APM izleme

---

## 13) Ek Kaynaklar

- `docs/odeme_rehberi.md` (PayTR entegrasyonu)
- `docs/roller_ve_yetkiler_kilavuzu.md` (Rol tanımları ve ekip yönetimi) **YENİ!**
- `docs/sirket_kayit_islem_kilavuzu.md` (Şirket kayıt süreci)
- `docs/kullanici_senaryolari.md` (Detaylı senaryolar)
- `docs/kullanici_senaryolari_ozet.md` (Özet)
- Django Admin ve DRF dokümantasyonu

---

Son güncelleme: Ekim 2025
