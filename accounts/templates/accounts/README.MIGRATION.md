# Accounts Templates Migration Guide

This guide describes the unified template architecture for the Accounts module after refactoring.

## 1. Base Hierarchy
- `core_ui/base.html` – Global site shell
- `core_ui/base_dashboard.html` – Generic dashboard frame (sidebar + header blocks)
- `accounts/base_accounts.html` – Accounts-specific mapping introducing semantic `acct_*` blocks

### acct_* Blocks
| Block | Purpose |
|-------|---------|
| `acct_title` | Primary page heading (maps to `dashboard_title`) |
| `acct_subtitle` | Supporting description (maps to `dashboard_subtitle`) |
| `acct_actions` | Action buttons area (maps to `dashboard_actions`) |
| `acct_content` | Main content area (maps to `dashboard_content`) |

Use these blocks instead of directly touching `dashboard_*` for clearer module semantics.

## 2. Sidebar
File: `accounts/partials/_sidebar.html`

Features:
- Grouped sections (Profil, Şirket, Abonelik, Rol Panelleri, Oturum)
- Active state via `p=request.path` and `{% with active=... %}` pattern
- `aria-current="page"` on active link for accessibility
- All labels wrapped with `{% trans %}` for internationalization

## 3. Dashboard Pages
Refactored pages extending `base_accounts.html`:
- `dashboard_kobi.html`
- `dashboard_egitimci.html`
- `dashboard_ogrenci.html`
- `dashboard_oyuncu.html`

Each overrides at least `acct_title`, `acct_subtitle`, and `acct_content`.

## 4. Profile & Company Pages
- `profile.html`, `company_detail.html`, `company_edit.html` now use the new blocks and consistent card components.
- Charts & data visualizations remain inside `acct_content` to avoid polluting hierarchy.

## 5. Subscription & Premium
- `change_subscription.html` enhanced with explicit field loop, inline error presentation, and translated labels.
- `premium_feature.html` now card-based with translatable status messaging.

## 6. Authentication Pages
- `login.html`, `register.html` refactored to extend `core_ui/base.html` (not the dashboard) for a neutral minimal layout.
- Rewritten with Bootstrap form groups, inline error handling, password toggle script (register page), and i18n.

## 7. Conventions
- Always load `{% load i18n %}` in templates with user-facing strings.
- Use `lead` class for introductory paragraphs; keep single `<h1>` via `acct_title`.
- Prefer explicit field loops over `{{ form.as_p }}` for accessibility and control.
- Group primary actions to the right with flex utilities (e.g., `d-flex justify-content-end gap-2`).

## 8. Adding a New Accounts Page
Example skeleton:
```django
{% extends 'accounts/base_accounts.html' %}
{% load i18n %}
{% block acct_title %}{% trans 'Yeni Sayfa' %}{% endblock %}
{% block acct_subtitle %}{% trans 'Kısa açıklama' %}{% endblock %}
{% block acct_actions %}
  <a href="#" class="btn btn-sm btn-primary">{% trans 'Eylem' %}</a>
{% endblock %}
{% block acct_content %}
  <div class="card shadow-sm"><div class="card-body">...</div></div>
{% endblock %}
```

## 9. Accessibility Notes
- Active sidebar link gets `aria-current`.
- Form errors surfaced with `.invalid-feedback` and always visible via `d-block`.
- Single logical heading path (h1 from title block; internal cards should use h2/h3 as needed).

## 10. Future Enhancements
- Replace path substring matching with `request.resolver_match.url_name` for active logic.
- Extract a reusable auth form partial if login/register variations grow.
- Add per-link permission checks if role-based visibility is required.

## 11. Testing
After modifying templates:
1. Run `pytest -q`
2. Navigate key pages to verify dark mode contrast + responsive layout
3. Confirm translation catalog updated (`makemessages`) for new strings.

---
Extend this guide as the module evolves.
