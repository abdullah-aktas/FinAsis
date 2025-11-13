# FinAsis Design Tokens & UI Rehberi

Bu doküman, `static/css/modern-ui.css` içinde kullanılan temel tasarım token’larını ve bileşen kütüphanesinin (navbar, footer, dashboard kartları vb.) Storybook/Figma eşleşmesini özetler. Tasarım ekibi yeni ekranları oluştururken ve geliştiriciler HTML/CSS tarafında düzenleme yaparken referans olarak kullanmalıdır.

## 1. Marka Renk Paleti

| Token                | Hex       | Kullanım Alanı                         |
|----------------------|-----------|----------------------------------------|
| `--brand-primary`    | `#0AAE94` | CTA butonları, aktif durumlar          |
| `--brand-secondary`  | `#667EEA` | Gradient ikincil ton, vurgu arka planı |
| `--brand-accent`     | `#764BA2` | Destekleyici vurgu, grafikler          |
| `--brand-success`    | `#10B981` | Pozitif rozetler, başarı bildirimleri  |
| `--brand-warning`    | `#F59E0B` | Uyarı, KPI düşüş trendi                |
| `--brand-danger`     | `#EF4444` | Kritik hata, negatif trend             |
| `--brand-info`       | `#3B82F6` | Bilgilendirme kartları                 |

### Nötr Tonlar

`--neutral-50` (`#F8FAFC`) ve `--neutral-900` (`#0F172A`) arasında uzanan skala; kart arka planı, border ve tipografi tonları için kullanılır.

## 2. Tipografi

- Ana font: `Inter` (400, 500, 600, 700)
- Boyut token’ları:
  - `--font-size-xs`: `0.75rem`
  - `--font-size-sm`: `0.875rem`
  - `--font-size-base`: `1rem`
  - `--font-size-lg`: `1.125rem`
  - `--font-size-xl`: `1.25rem`
  - `--font-size-2xl`: `1.5rem`
  - `--font-size-3xl`: `1.875rem`
  - `--font-size-4xl`: `2.25rem`

Başlıklar için 700–800 arası ağırlık, gövde metinleri için 400–500 önerilir.

## 3. Spacing & Radius

- Spacing: `--spacing-xs` (`4px`) → `--spacing-3xl` (`64px`)
- Border radius:
  - `--radius-sm`: `6px`
  - `--radius-md`: `8px`
  - `--radius-lg`: `12px`
  - `--radius-xl`: `16px`
  - `--radius-2xl`: `24px`

Dashboard hero ve kartlarında clamp değerleri kullanılarak responsive radius uygulanır. Özel durumlarda stil dosyasında `clamp()` ile override edilebilir.

## 4. Bileşen Kütüphanesi & Figma Eşlemesi

| Kod Bileşeni                      | CSS Sınıfı / Token                     | Figma / Storybook Referansı            |
|-----------------------------------|----------------------------------------|----------------------------------------|
| Navbar (ana menü)                 | `.navbar`, `.btn-modern`               | “Navigation / Top Bar”                 |
| Footer (kurumsal & app)           | `.corporate-footer`, `.brand-badge`    | “Global / Footer”                      |
| Dashboard hero                    | `.dashboard-hero`, `.persona-hero`     | “Dashboards / Hero Section”            |
| KPI kartları                      | `.dashboard-kpi-card`, `.stat-card`    | “Dashboards / KPI Cards”               |
| Aksiyon kartları                  | `.dashboard-action-card`               | “Dashboards / Quick Actions”           |
| Resource Hub kartları             | `.resource-card`, `.playbook-card`     | “Resources / Tile Grid”                |
| AI öneri kartı (planlanan)        | `.ai-suggestion-card` (eklenecek)      | “Assistants / Suggestion Card”         |
| Form elemanları                   | `.form-modern`                         | “Forms / Controls”                     |
| Bildirim & rozetler               | `.alert-modern`, `.badge-modern`       | “Feedback / Alerts & Tags”             |

> Not: Storybook henüz repo içinde değil; bileşen isimleri Figma katman adlarıyla eşitlenerek tasarım ekibi tarafından yönetiliyor. Kod tarafında sınıf isimlerini değiştirmeden yeni varyantlar için modifier sınıfları (`--warm`, `--neutral` gibi) kullanılmalı.

## 5. İkon Seti

- Kullanılan ikon kütüphanesi: Bootstrap Icons (`cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3`).
- Figma’da “Iconography / Bootstrap” sayfasında aynı isimde komponentler bulunur.
- Emphasis durumlarında ikon rengi:
  - Primary highlight: `var(--brand-primary)`
  - Uyarı: `var(--brand-warning)`
  - Başarı: `var(--brand-success)`

## 6. Motion & Shadow

- Transition token’ları:
  - `--transition-fast`: `150ms ease-in-out`
  - `--transition-base`: `200ms ease-in-out`
  - `--transition-slow`: `300ms ease-in-out`
- Shadow token’ları (`--shadow-sm`, `--shadow-md`, `--shadow-lg`, `--shadow-xl`) bileşenler arası derinlik hiyerarşisini belirler.

## 7. Kullanım İlkeleri

1. **Inline CSS** yerine mutlaka `static/css/modern-ui.css` veya ilgili `pages/*.css` dosyalarında tanımlı sınıfları kullanın. Yeni sayfa bazlı varyant gerekiyorsa component sınıfını genişleten modifier yazın (`.dashboard-section-card--warm` gibi).
2. **CSS değişiklikleri** yaparken Figma bileşeninin ismini commit mesajında belirtin; tasarım ekibi eş zamanlı güncelleyebilsin.
3. **Responsive davranış** için `clamp()` ve CSS değişkenleri tercih edin. 768px altı için grid yapıları otomatik tek sütuna düşmeli.
4. **Erişilebilirlik**: Kontrastı düşük metinler için nötr tonları (ör. `--neutral-600`) seçin; `btn-modern` varyantlarında focus durumuna `box-shadow` eklendi.

---

Bu kılavuz, tasarım sistemi büyüdükçe güncellenecektir. Ek bileşenler veya token talepleri için Jira’daki “DS-Board” üzerinden issue açabilirsiniz. Git repo tarafında yeni bileşen dosyaları eklerken `static/css/components/` klasör hiyerarşisi kullanılmalıdır (planlı genişletme). Figma linki: `https://www.figma.com/file/FINASIS/design-system` (erişim için FinAsis hesabı gerekir).

