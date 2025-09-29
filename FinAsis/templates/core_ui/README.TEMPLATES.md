# FinAsis Template Sistemi (Core UI)

Bu klasör yeni birleşik şablon mimarisini içerir.

## Ana Dosyalar
- `base.html`: Genel site ve kamuya açık sayfalar için temel şablon. SEO meta, tema toggle, mesajlar, breadcrumb ve çerez onayı içerir.
- `base_dashboard.html`: Uygulama içi (oturum açmış) panel sayfaları için. Sol yan menü + başlık blokları sunar.

## Parçalar
- `partials/_analytics.html`: Analytics betiği (ID üretim ortamında değiştirilmelidir).
- `partials/_cookie_consent.html`: Basit çerez onayı bileşeni (localStorage tabanlı).
- `partials/_breadcrumbs.html`: `breadcrumbs` context listesine göre dinamik gezinme yolu.
- `components/messages.html`: Tekilleştirilmiş uyarı / feedback sistemi.

## Tema ve Marka
- `static/css/brand.css` dosyası marka renk değişkenleri ve dark mode destekler.
- Tema toggle: Header içinde `toggleTheme()` fonksiyonu ve localStorage anahtarı `finasis_pref_theme`.
- Hızlı kısayol: `Ctrl + D` tema değiştirir.

## Blok Yapısı (base.html)
- `title`, `meta_description`
- `extra_head`, `extra_css`, `extra_js`
- `header`, `hero`, `breadcrumbs`, `content`, `footer`
- `main_class` ile `<main>` ek sınıflar eklenebilir.

## Geçiş (Migration)
- Eski `common/base.html` artık sadece `core_ui/base.html` genişletir.
- Eski root `templates/base.html` dosyası silinebilir veya yönlendirme amaçlı tutulabilir (henüz kaldırılmadı).
- Yeni şablon yazarken doğrudan `{% extends 'core_ui/base.html' %}` kullanın.
- Dashboard içerikleri için `{% extends 'core_ui/base_dashboard.html' %}` tercih edin.

## Breadcrumb Örneği
View context:
```python
context['breadcrumbs'] = [
  {'label': 'Panel', 'url': '/dashboard/'},
  {'label': 'Raporlar', 'url': '/dashboard/reports/'},
  {'label': 'Gelir Analizi'}  # son eleman aktif olur
]
```

## Mesaj Sistemi
Django `messages` framework mesajları otomatik olarak gösterilir.
- Desteklenen etiketler: `success`, `error`/`danger`, `warning`, diğerleri `info`.

## Geliştirme Notları / Yol Haritası
- [ ] Yüksek erişilebilirlik (ARIA canlı bölgeyi toast için eklemek)
- [ ] Lazy load grafik / ağır JS (Intersection Observer)
- [ ] Header arama önerileri (AJAX)
- [ ] Komponent bazlı CSS ayrıştırması (SCSS -> static build pipeline)

---
Sorular için: `core_ui` maintainer.
