# AI Assistant Template Migration Guide

This document explains the refactor of AI Assistant templates into the unified design system.

## Goals
- Consistent layout with other modules (Accounting, Accounts)
- Semantic block layer (`ai_*`) mapped onto shared dashboard blocks
- Accessibility (ARIA, headings, live regions)
- Internationalization safe patterns (no `{% trans %}` inside dynamic JS expressions)
- Reusable components: sidebar, table layout, empty states, messages
- Dark mode friendly (CSS variables + system tokens)

## Base Template
`ai_assistant/base_ai_assistant.html` extends `core_ui/base_dashboard.html` and maps:
- `ai_title` -> `dashboard_title`
- `ai_subtitle` -> `dashboard_subtitle`
- `ai_actions` -> `dashboard_actions`
- `ai_content` -> `dashboard_content`

Use these semantic blocks in all AI module templates instead of the dashboard block names directly.

## Sidebar
`ai_assistant/partials/_sidebar.html` contains navigation. Active states use `request.path` checks and `aria-current="page"` where appropriate. Keep link text wrapped in `{% trans %}`.

## Refactored Templates
- `home.html`
- `chat.html`
- `financialprediction_list.html`
- `recommendation_list.html`
- `analysis.html`
- `forecast_dashboard.html`

All now extend `base_ai_assistant.html` and fill the semantic `ai_*` blocks.

## Lists & Tables Pattern
Each list page uses a consistent structure:
1. Local filter form (method="get")
2. Responsive table container (`table-responsive`)
3. Table with translatable headers
4. Empty state if queryset/table is empty (aria-live polite)
5. Pagination (reuse existing shared partial if consolidated later)

## JavaScript i18n Pattern
Avoid placing `{% trans %}` directly inside template literals with nested expressions. Instead:
1. Define top-level constants:
   ```js
   const TXT_DELETE_ROW = "{% trans 'Satırı Sil' %}";
   ```
2. Use these constants when building dynamic HTML or messages.
3. Escape any user/data-originated content when injecting into `innerHTML` (see `escapeHtml`).

## Accessibility Notes
- Use `aria-live="polite"` for dynamic content regions (e.g. error messages, model info)
- Provide `aria-label` on interactive buttons without full text labels or where icon-only
- Ensure table headers use `<th scope="col">`
- Maintain logical heading order (`h1` in dashboard header, then `h2/h5` within content)

## Dark Mode
Colors rely on `var(--bs-*)` tokens. Avoid hard-coded hex where possible. When necessary, provide sufficient contrast and consider adding a dark variant inside a `@media (prefers-color-scheme: dark)` clause.

## Security: HTML Injection
When inserting data-driven content (e.g. model parameters, explanation features) use an `escapeHtml` helper to prevent injection.

## Adding New Pages
1. Create template extending `ai_assistant/base_ai_assistant.html`.
2. Set `ai_title`, `ai_subtitle` blocks.
3. Add content in `ai_content` block. Prefer existing component classes.
4. Add any page-specific styles in `extra_css` (scoped selectors) and scripts in `extra_js`.
5. Follow JS i18n constant pattern.

## Future Enhancements (Backlog)
- Extract shared filter form partial for AI list pages
- Centralize pagination partial reuse
- Add automated tests for forecast & analysis views
- Integrate server-side streaming for chat updates

## Changelog
- 2025-09-30: Initial migration & documentation created.

---
Maintainers: Update this guide whenever a structural convention changes.
