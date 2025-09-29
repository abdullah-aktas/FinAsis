# Accounting Templates Migration Guide

This guide documents the new unified template architecture for the Accounting module and how to migrate or add new views consistently.

## 1. Layered Base Structure

Base inheritance chain:
- `core_ui/base.html` – Global site chrome (head tags, messages, theming, footer hooks)
- `core_ui/base_dashboard.html` – Dashboard layout wrapper (header, container, optional sidebar slot)
- `accounting/base_accounting.html` – Injects accounting sidebar and defines `acc_*` semantic blocks

### acc_* Blocks
Use these high-level blocks to structure each accounting page:
- `acc_title` – Page heading (h1) text
- `acc_subtitle` – Optional supporting description below the title
- `acc_actions` – Primary/secondary action buttons (aligned to the right in header row)
- `acc_content` – Main content area (tables, forms, cards, reports)

Each template typically overrides at minimum: `acc_title` and `acc_content`.

## 2. Sidebar Navigation
File: `partials/_sidebar.html`

Enhancements:
- Active link styling + `aria-current="page"` for accessibility
- All labels wrapped with `{% trans %}` for i18n
- Section headings (e.g. Genel, Kayıtlar, Ödemeler) remain uppercase muted typographic anchors

When adding a new section:
1. Group related links under a translated heading
2. Use a `{% with active=... %}` block for clarity
3. Add `{% trans 'Label' %}` around the visible text

## 3. Reusable Partials
| Partial | Purpose |
|---------|---------|
| `partials/_form.html` | Consistent form rendering (fields loop, errors, help text, CSRF) |
| `partials/_pagination.html` | Standardized pagination (prev/next, page numbers, disabled states) |
| `components/messages.html` (global) | Unified Django messages styling |
| `_breadcrumbs.html` (core) | Optional hierarchical navigation; pass `breadcrumbs` var |

### Usage Examples
```
{% include 'accounting/partials/_form.html' with form=form submit_label=_('Kaydet') %}
{% include 'accounting/partials/_pagination.html' with page_obj=page_obj %}
```

## 4. List Template Pattern
All list (index) pages follow a consistent anatomy:
1. Filter Form (inline or collapsible) – Reflects GET parameters
2. Responsive table with `table table-sm align-middle` classes
3. Empty State – Shown when `object_list|length == 0`
4. Pagination Include – Bottom of content (`_pagination.html`)

### Empty State Pattern
```
{% if not object_list %}
  <div class="text-center p-5 border rounded bg-body-tertiary">
    <div class="display-6 mb-3">😐</div>
    <p class="lead mb-3">{% trans 'Kayıt bulunamadı.' %}</p>
    <a href="{{ create_url }}" class="btn btn-primary">{% trans 'Yeni Oluştur' %}</a>
  </div>
{% endif %}
```

## 5. Breadcrumbs
Breadcrumbs are optional. Provide a list of dicts via view context:
```
context['breadcrumbs'] = [
  {'label': _('Muhasebe'), 'url': reverse('accounting:home')},
  {'label': _('Faturalar')},
]
```
The current page omits `url`.

## 6. Internationalization (i18n)
Wrap static UI strings with `{% trans %}` or `{{ _('Text') }}` (if `ugettext` available in context). Keep placeholders outside translation tags when interpolating variables.

## 7. Adding a New Page
1. Create `<feature>_list.html` or `<feature>_detail.html` under `accounting/`
2. Start with:
```
{% extends 'accounting/base_accounting.html' %}
{% load i18n %}

{% block acc_title %}{% trans 'Yeni Özellik' %}{% endblock %}

{% block acc_content %}
  <div class="card shadow-sm">
    <div class="card-body">
      <!-- content -->
    </div>
  </div>
{% endblock %}
```
3. If list view, add filter form + table + empty state + pagination include.
4. Add navigation link in `_sidebar.html` with translated label and active logic.

## 8. Reports Landing Pattern
`reports_landing.html` aggregates report entry-points using a grid of cards with:
- Icon (Bootstrap icons)
- Title (translatable)
- Short description (translatable)
- CTA buttons (disabled or active depending on implementation status)

## 9. Accessibility Notes
- `aria-current="page"` automatically added to active sidebar links.
- Ensure tables include `<thead>` and scoped header cells `<th scope="col">`.
- Use semantic headings: Only one `<h1>` per view (provided via `acc_title`).

## 10. Testing & Consistency
After adding or modifying templates:
- Run `pytest -q` to ensure no template resolution errors
- Visually verify dark mode adherence (tokens defined in `brand.css`)
- Confirm translations compile (if `makemessages` / `compilemessages` used)

## 11. Future Enhancements (Optional)
- Extract a filters macro/partial for repetitive list filter forms
- Add role="navigation" landmarks around sidebar nav (currently implied by `<nav>`)
- Introduce per-link permission checks (wrap anchors with `{% if perms.app_label.permission_codename %}`)

---
Questions or improvements? Extend this guide to keep architectural clarity high.
