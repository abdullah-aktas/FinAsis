# Core UI (FinAsis Kurumsal Arayüz Bileşenleri)

Bu uygulama FinAsis projesi içinde kurumsal görünüm ve tekrar kullanılabilir temel şablonları sağlar.

## İçerik
- `templates/core_ui/base.html` : Tüm sayfaların genişleteceği temel layout
- `templates/core_ui/components/*` : Navbar, mesajlar vb. parçalar
- `static/core_ui/js/theme-toggle.js` : Karanlık mod anahtarı
- `templatetags/core_ui.py` : Mesaj bileşeni inclusion tag

**Not:** Footer component'i `templates/components/footer.html` içinde bulunmaktadır. Corporate CSS dosyası `static/css/pages/corporate.css` içinde bulunmaktadır.

## Kullanım
Bir template dosyasında:
```django
{% extends 'core_ui/base.html' %}
{% block title %}Sayfa Başlığı{% endblock %}
{% block content %}
  <h1>İçerik</h1>
{% endblock %}
```

## Bloklar
- `title`, `meta_description`, `meta_keywords`
- `head_extra` : `<head>` içine ek içerik
- `extra_css` / `extra_js` : Harici stil & script ekleme
- `breadcrumbs` : Ekmek kırıntısı navigasyonu
- `content` : Ana içerik

## Tema
`body[data-theme="dark"]` attribute ile karanlık mod etkinleşir. JS otomatik olarak `localStorage` üzerinden tercihleri hatırlar.

## Geliştirme Notları
- Yeni bir component eklerken `templates/core_ui/components/` altına koyun ve `base.html` içinden include edin.
- Statik dosyaları `static/core_ui/` altına koyun.
- Paketleme veya dış projede kullanım için app `INSTALLED_APPS` listesine eklenmelidir (bu projede eklendi).
