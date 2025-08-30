# FinAsis Statik Dosya ve UI Kılavuzu

## 1. Logo Kullanımı
- `FinAsis_logo.png`: Açık zeminlerde, orijinal renkli logo.
- `FinAsis_logo_white.svg`: Koyu arka planlarda beyaz logo.
- Logonun etrafında minimum logonun yüksekliği kadar boşluk bırakılmalı.
- Logonun oranı, rengi ve opaklığı değiştirilmemelidir.

## 2. Renk Paleti
| Renk Adı         | HEX      | Kullanım Alanı                       |
|------------------|----------|--------------------------------------|
| Birincil         | #00B894  | Butonlar, vurgular, grafik           |
| İkincil          | #263238  | Başlıklar, yazılar                   |
| Açık Yeşil       | #F7FDFB  | Arka plan, form alanları             |
| Aksiyon (Sarı)   | #FFC107  | Uyarı, badge, hover                  |
| Grafik Vurgusu 1 | #6366F1  | Grafik çizgileri, interaktif UI      |
| Grafik Vurgusu 2 | #00CEC9  | Sekmeler, tooltip arka planları      |
| Karanlık BG      | #121212  | Gece modu arka plan                  |
| Karanlık Yazı    | #EAEAEA  | Gece modu yazılar                    |

## 3. Tipografi
- Başlıklar: `Inter`, Alternatif: Roboto, Poppins (600–800)
- Gövde: `Open Sans`, Alternatif: Roboto (400–600)
- Kod: `Fira Code`, Alternatif: Courier New
- Boyutlar: H1: 36px, H2: 28px, Body: 16px, Küçük: 14px

## 4. Görsel Dil & Stil
- İllüstrasyonlar: Yarı gerçekçi, çizgisel, marka renklerinde
- İkonlar: Bootstrap Icons (outline), dolgusuz, başlık rengine uygun

## 5. Butonlar & Komponentler
- Birincil: #00B894 zemin, beyaz yazı, oval (50px)
- İkincil: Beyaz zemin, #00B894 yazı ve kenar
- Badge: #FFC107 zemin, siyah yazı
- Tüm butonlar: padding 0.75rem 2rem, font-size 16px+

## 6. Responsive & Mobil
- Dashboard grid mobilde tek sütun
- Hamburger menü ve swipe kart desteği

## 7. Dark Mode
- Dark mode için body'ye `data-theme="dark"` eklenir.
- Renk değişkenleri otomatik değişir.

## 8. Lisans
- Tüm dosyalar sadece FinAsis projesi kapsamında kullanılabilir.
- Değişiklikler için tasarım onayı gereklidir.

# Statik Dosya Yönetimi (static/ ve staticfiles/)

Bu klasör, FinAsis projesinin tüm frontend varlıklarını (CSS, JS, görseller, ikonlar, dil dosyaları, PWA dosyaları) içerir.

## Klasör Yapısı
- `common/` : Ortak görseller, logolar, favicon, genel CSS/JS dosyaları
- `js/` : Ortak JavaScript dosyaları (örn. i18n, tema, erişilebilirlik)
- `css/` : Ortak CSS dosyaları (tema, responsive, a11y, rtl)
- `components/` : HTML component parçaları (örn. cookie consent, language select)
- `locales/` : Çoklu dil desteği için JSON dosyaları (tr, en, de, fr, ar, ku)
- `manifest.json` : PWA için manifest dosyası
- `LICENSE.txt` : Statik varlıklar için lisans

## Uygulama Bazlı Statik Dosyalar
Her uygulama (ör. accounting, finance, ai_assistant) kendi statik dosyalarını `apps/uygulama_adi/static/uygulama_adi/` altında tutmalıdır. Bu, modülerlik ve bakım kolaylığı sağlar.

## staticfiles/ Klasörü
- **Sadece otomatik olarak** `python manage.py collectstatic` komutu ile güncellenir.
- Elle dosya eklemeyin veya silmeyin.
- Deployment ortamında (örn. production sunucusu, CDN) sadece bu klasör kullanılır.

## En İyi Pratikler
- Ortak kullanılan dosyaları sadece `static/common/` altında tutun.
- Uygulama bazlı dosyaları kendi klasöründe tutun.
- `collectstatic` komutunu deployment öncesi mutlaka çalıştırın.
- Çoklu dil desteği için `locales/` klasörünü kullanın.
- PWA, manifest, service worker gibi dosyaları ana static altında bulundurun.
- Statik dosya yollarını Django template tag'leri ile çağırın: `{% static 'common/FinAsis_logo.png' %}`

## Örnek Kullanım
```html
<img src="{% static 'common/FinAsis_logo.png' %}" alt="Logo">
<link rel="stylesheet" href="{% static 'css/main.css' %}">
<script src="{% static 'js/main.js' %}"></script>
```

## Notlar
- Statik dosyalarınızda değişiklik yaptıktan sonra, deployment ortamında tekrar `collectstatic` çalıştırmayı unutmayın.
- CDN veya reverse proxy kullanıyorsanız, `staticfiles/` klasörünü sunucuya veya CDN'e yükleyin. 