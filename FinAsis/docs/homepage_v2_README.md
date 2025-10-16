# FinAsis Anasayfa v2.0 - Kurulum ve Kullanım Rehberi

## 📋 Özet

FinAsis anasayfası modern, kullanıcı dostu, kurumsal bir tasarımla yeniden oluşturuldu.

**Temel Özellikler:**
- ✨ Modern, temiz, profesyonel tasarım
- 🎨 Yeşil-Lacivert-Turuncu renk paleti
- 📱 Responsive design (mobile-first)
- ♿ WCAG 2.1 AA erişilebilirlik
- 🚀 Performans odaklı
- 🧩 Modüler component yapısı

---

## 📁 Oluşturulan Dosyalar

### 1. Template Dosyaları

#### `templates/home.html` (Güncellendi)
```django
{% extends "core_ui/base.html" %}
{% load static i18n %}

{% block extra_css %}
  <link rel="stylesheet" href="{% static 'css/design-system.css' %}">
{% endblock %}

{% block content %}
  {% include 'components/home_sections_v2.html' %}
{% endblock %}
```

**Değişiklikler:**
- Design system CSS eklendi
- SEO meta tags güncellendi
- Yeni component referansı: `home_sections_v2.html`

#### `templates/components/home_sections_v2.html` (Yeni)

**8 Major Bölüm:**

1. **Hero Section** - Gradient arka plan, ROI calculator
2. **Social Proof** - Müşteri logoları (500+ işletme)
3. **Features** - 6 özellik kartı
4. **Stats** - 4 istatistik (işletme, fatura, memnuniyet, destek)
5. **How It Works** - 3 adım (Kayıt, Bilgi, Kullanım)
6. **Testimonials** - 3 müşteri yorumu
7. **Pricing Teaser** - 3 fiyat planı
8. **Final CTA** - Harekete geçirme bölümü

### 2. CSS Dosyası

#### `frontend/static/css/design-system.css` (Yeni)

**İçerik:**
- 650+ satır CSS
- 48 CSS custom property
- Tüm component stilleri
- Animasyonlar
- Accessibility özellikleri
- Responsive media queries

---

## 🚀 Kurulum

### Adım 1: Dosyaların Varlığını Kontrol Edin

```bash
# Dosyaların yerinde olduğunu doğrulayın
ls templates/home.html
ls templates/components/home_sections_v2.html
ls frontend/static/css/design-system.css
```

### Adım 2: Static Dosyaları Toplayın

```bash
python manage.py collectstatic --noinput
```

### Adım 3: Sunucuyu Başlatın

```bash
python manage.py runserver
```

### Adım 4: Tarayıcıda Açın

```
http://localhost:8000/
```

---

## 🎨 Tasarım Sistemi

### Renk Paleti

```css
--color-primary: #10b981     /* Yeşil (Ana renk) */
--color-secondary: #1e293b   /* Lacivert (İkincil renk) */
--color-accent: #f59e0b      /* Turuncu (Vurgu rengi) */
```

### Typography

- **Font Family:** Inter (Sans-serif)
- **Font Weights:** 400 (Normal), 500 (Medium), 600 (Semibold), 700 (Bold), 800 (Extrabold)
- **Base Size:** 16px (1rem)

### Spacing

```css
--spacing-1: 0.25rem   /* 4px */
--spacing-2: 0.5rem    /* 8px */
--spacing-3: 0.75rem   /* 12px */
--spacing-4: 1rem      /* 16px */
--spacing-5: 1.5rem    /* 24px */
--spacing-6: 2rem      /* 32px */
```

---

## 🧩 Component Kullanımı

### Buttons

```html
<!-- Primary Button -->
<a href="#" class="btn corporate-btn-primary">
  <i class="bi bi-rocket-takeoff me-2"></i>
  Hemen Başla
</a>

<!-- Secondary Button -->
<a href="#" class="btn corporate-btn-secondary">
  <i class="bi bi-person-plus me-2"></i>
  Kayıt Ol
</a>

<!-- Preset Button -->
<button class="btn corporate-btn-preset">
  <i class="bi bi-star me-1"></i>
  Başlangıç
</button>
```

### Cards

```html
<!-- Feature Card -->
<div class="card corporate-feature-card">
  <div class="card-body">
    <div class="corporate-feature-icon mb-3">
      <i class="bi bi-graph-up-arrow"></i>
    </div>
    <h4 class="fw-bold mb-2">Başlık</h4>
    <p class="text-muted">Açıklama...</p>
  </div>
</div>

<!-- Pricing Card -->
<div class="card corporate-pricing-card">
  <div class="card-body p-4">
    <h4 class="fw-bold mb-2">Plan Adı</h4>
    <div class="display-4 fw-bold">499₺</div>
    <div class="text-muted">/ay</div>
  </div>
</div>
```

### Badges

```html
<!-- New Badge -->
<span class="badge corporate-badge-new">
  <i class="bi bi-stars me-1"></i>
  Yeni · v2.0
</span>

<!-- Section Badge -->
<span class="badge corporate-badge-secondary">
  Özellikler
</span>

<!-- Popular Badge (on pricing card) -->
<div class="corporate-popular-badge">Popüler</div>
```

---

## 📊 ROI Calculator

### HTML Yapısı

```html
<div class="corporate-roi-calculator card">
  <!-- Header -->
  <div class="corporate-calculator-icon">
    <i class="bi bi-graph-up-arrow"></i>
  </div>
  
  <!-- Preset Buttons -->
  <button data-roi-preset data-cost="499" data-hours="20" data-rate="300">
    Başlangıç
  </button>
  
  <!-- Form Inputs -->
  <input id="roiCost" type="number" placeholder="1599">
  <input id="roiHours" type="number" placeholder="40">
  <input id="roiRate" type="number" placeholder="400">
  
  <!-- Calculate Button -->
  <button id="roiCalc">Hesapla</button>
  
  <!-- Result Display -->
  <div id="roiResult">...</div>
</div>
```

### JavaScript Mantığı

```javascript
// Hesaplama:
const saving = hours * rate;          // Tasarruf
const net = saving - cost;            // Net kazanç
const roi = (net / cost * 100);       // ROI yüzdesi

// Örnek: 1599₺ lisans, 40 saat tasarruf, 400₺/saat
// Saving: 40 × 400 = 16,000₺
// Net: 16,000 - 1,599 = 14,401₺
// ROI: (14,401 / 1,599) × 100 = %900
```

---

## 🔗 URL Yapılandırması

Aşağıdaki URL'lerin mevcut olduğundan emin olun:

```python
# urls.py
urlpatterns = [
    path('', views.home, name='home'),
    path('billing/plans/', include('billing.urls', namespace='billing')),
    path('accounts/register/', include('accounts.urls', namespace='accounts')),
    path('contact/', views.contact, name='contact'),
]
```

---

## ✅ Checklist: Yayına Alma Öncesi

### İçerik Güncellemeleri

- [ ] Gerçek müşteri logolarını ekle (`static/brand/client-logo-[1-5].svg`)
- [ ] Testimonial fotoğraflarını ekle (`static/brand/avatar-*.jpg`)
- [ ] Tüm CTA linklerini doğrula
- [ ] ROI calculator default değerlerini güncelle

### Teknik Kontroller

- [ ] `collectstatic` çalıştır
- [ ] CSS minify et (production için)
- [ ] Görsel optimizasyonu yap (WebP)
- [ ] Lighthouse audit yap (Performance, SEO, Accessibility)
- [ ] Cross-browser test (Chrome, Firefox, Safari, Edge)
- [ ] Mobile test (iOS, Android)

### SEO

- [ ] Meta tags güncelle
- [ ] Open Graph tags ekle
- [ ] Twitter Card tags ekle
- [ ] Sitemap.xml güncelle
- [ ] robots.txt kontrol et

### Analytics

- [ ] Google Analytics tracking ekle
- [ ] CTA click tracking ekle
- [ ] ROI calculator usage tracking ekle
- [ ] Form submission tracking ekle

---

## 🐛 Troubleshooting

### CSS Yüklenmiyor

**Sorun:** Stiller görünmüyor
**Çözüm:**
```bash
python manage.py collectstatic --noinput
# Tarayıcı cache'ini temizle (Ctrl + Shift + R)
```

### ROI Calculator Çalışmıyor

**Sorun:** JavaScript hata veriyor
**Çözüm:**
- Tarayıcı console'u kontrol et (F12)
- Element ID'lerinin doğru olduğundan emin ol:
  - `roiCost`, `roiHours`, `roiRate`, `roiCalc`, `roiResult`

### Bootstrap Icons Görünmüyor

**Sorun:** İkonlar görünmüyor
**Çözüm:**
```html
<!-- base.html içinde olduğundan emin ol -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
```

### Responsive Sorunları

**Sorun:** Mobile'da düzen bozuk
**Çözüm:**
```html
<!-- Viewport meta tag olduğundan emin ol -->
<meta name="viewport" content="width=device-width, initial-scale=1">
```

---

## 📚 Daha Fazla Bilgi

- **Tasarım Sistemi:** `docs/design_system_guide.md`
- **Component Örnekleri:** `templates/components/home_sections_v2.html`
- **CSS Referansı:** `frontend/static/css/design-system.css`

---

## 🤝 Katkıda Bulunma

Yeni component veya stil eklerken:

1. CSS custom properties kullan
2. BEM metodolojisine uy (`corporate-block__element--modifier`)
3. Responsive design uygula (mobile-first)
4. Accessibility standartlarına uy (WCAG 2.1 AA)
5. Dokümante et

---

## 📞 Destek

Sorularınız için:
- 📧 design@finasis.com.tr
- 💬 Slack: #design-system
- 📖 Wiki: Design System Documentation

---

**Son Güncelleme:** 15 Ekim 2025
**Versiyon:** 2.0
**Durum:** ✅ Production Ready
