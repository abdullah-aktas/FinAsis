# PR Plan (Small, Focused PRs)

Each PR includes purpose/scope, changed files, acceptance tests, and compatibility notes.

## PR-1: AuditEvent Universal Signals

- Purpose: Introduce unified `AuditEvent` capturing CRUD and auth events with rich meta and diffs.
- Scope:
  - New app module `apps/audit/` with `models.py` (`AuditEvent`), `signals.py`, `middleware.py` (request meta capture), `utils.py` (diff), `admin.py`, `migrations/0001_initial.py`.
  - Hook signals for post_save/post_delete across critical models (finance.accounting, banking, einvoice, permissions, virtual_company).
  - Capture auth login/logout via Django signals.
  - Wire into settings INSTALLED_APPS and middleware.
- Acceptance Criteria (tests):
  - `tests/test_audit_events.py::test_create_update_delete_logged`
  - `tests/test_audit_events.py::test_auth_login_logout_logged`
  - `tests/test_audit_events.py::test_meta_includes_ip_ua_tenant`
- Compatibility: additive migration; no breaking changes.

## PR-2: LedgerAnchor & Blockchain Service

- Purpose: Add `LedgerAnchor` model and JSON canonicalization pipeline to compute SHA-256 and persist with optional async write and `txn_hash`.
- Scope:
  - `apps/blockchain/models.py`: add `LedgerAnchor` with fields: model, record_id, normalized_json, hash_hex, status, txn_hash, created_at.
  - `apps/blockchain/services.py`: `normalize(instance)`, `compute_sha256()`, `enqueue_anchor_write(anchor_id)` (Celery stub or sync fallback), verify function.
  - `apps/blockchain/views.py`: `GET /api/v1/blockchain/verify?model=&id=`.
  - urls under `apps/blockchain/urls.py` add API route.
  - migrations.
- Acceptance Criteria (tests):
  - `tests/test_anchor.py::test_normalize_and_hash_deterministic`
  - `tests/test_anchor.py::test_verify_endpoint_ok`
- Compatibility: additive; no schema conflicts; optional Celery.

## PR-3: RBAC Hooks

- Purpose: Enforce Role→Permission→Resource on DRF endpoints and restrict menu visibility.
- Scope:
  - `api/permissions.py`: `HasResourcePermission` reading from `permissions` app models.
  - Apply to DRF viewsets (permissions, management API, games APIs, finance APIs).
  - Helpers to compute required resource/action per view.
  - Template context processor or tags to hide menu items.
- Tests:
  - `tests/test_rbac.py::test_view_denied_without_permission`
  - `tests/test_rbac.py::test_view_allowed_with_permission`
- Compatibility: minor template changes; additive.

## PR-4: Reports (MVP)

- Purpose: Trial Balance (Mizan) and Income Statement with date/tenant filters and cache.
- Scope:
  - `reports/queries.py` with ORM/SQL helpers.
  - `apps/finance/accounting/views_reports.py` endpoints and templates.
  - Per-tenant cache keys and tests/fixtures.
- Tests:
  - `tests/test_reports.py::test_trial_balance_correct`
  - `tests/test_reports.py::test_income_statement_tenant_date_filters`
- Compatibility: additive.

## PR-5: Flet Mobile Flows

- Purpose: Implement Flet routes /login, /dashboard, /invoice/new, /audit, /edu with API service layer and error snackbars.
- Scope:
  - `flet_mobile/` package: `main.py`, `routes.py`, `pages/*.py`, `services/api.py`.
- Tests: minimal smoke test
- Compatibility: additive.
