# FinAsis Gap Analysis (Health Check)

Risk levels: High / Medium / Low. File:line references use active code under `FinAsis/apps/*` and `FinAsis/config/*`.

## Multi-tenant

- Missing tenant isolation fields on most models (no `tenant_id` or company scoping standard). Example models without explicit tenant: `apps/common/models.py:6-31` AuditLog (no tenant), `apps/blockchain/models.py:1-15` ChainRecord (no tenant). Risk: High.
- Views/Querysets rarely filter by tenant/company consistently. Example: `apps/virtual_company/views.py` viewsets set `permission_classes` but no `get_queryset` tenant filter. Risk: High.
- File storage and cache use global paths: `config/settings.py:177-185` file-based cache without tenant prefix. Risk: Medium.

## RBAC / Authorization

- DRF ViewSets in permissions app use `IsAuthenticated` only (e.g., `apps/permissions/views.py:208,220,242,270,288,300,312,324,336,348,360,372,384,396,408,422`). No resource-based permission checks. Risk: High.
- Many app endpoints mounted directly in `config/urls.py` without auth requirements on views (marketing pages OK; admin-like pages must be verified). Risk: Medium.
- No centralized permission classes mapping Role→Permission→Resource for DRF. Risk: High.

## Audit Trail

- There is a `Common.AuditLog` model and ad-hoc logging via `log_action` in some views: `apps/common/views.py:16,24,27`. But no universal CRUD signals across models; many "AUDIT: print(...)" statements in `apps/virtual_company/views.py:39,47,117`. Risk: High.
- Auth events (login/logout) not captured to audit. Risk: High.
- No diff capture between updates. Risk: Medium.

## Blockchain Anchor

- Present minimal anchor: `ChainRecord` model (`apps/blockchain/models.py`) + SHA-256 deterministic payload helpers (`apps/blockchain/services.py`). Signals attach to finance events (`apps/blockchain/signals.py`). Good base.
- No external Besu/Quorum client integration; no `txn_hash` on model; no verification endpoint. Risk: Medium.
- Payloads are stable strings but not JSON-normalized with sorted keys; OK for MVP but should standardize to JSON canonicalization. Risk: Medium.

## API Contract

- No unified `/api/v1/` prefix or versioning in `config/urls.py`. Risk: Medium.
- Pagination/filtering behaviors vary per view; not enforced globally with DRF settings. Risk: Medium.
- Idempotency-Key headers not handled on POST endpoints. Risk: Low/Medium.

## Reports

- General ledger views exist (`apps/finance/accounting/urls.py:82,107`, views around export) but no clear Trial Balance (Mizan) and Income Statement endpoints with tenant/date filters and per-tenant cache. Risk: Medium.

## Flet

- No `flet_mobile` package found; Flet flows not implemented. Risk: Medium.

## Tests & Security

- Tests are mostly Playwright-style UI crawl/accessibility under `FinAsis/tests/*`; minimal unit tests for finance/domain/permissions. Risk: High.
- OWASP ASVS checks not automated. Risk: Medium.
- Settings: SECRET_KEY read from env (good), DEBUG env-controlled (good). CACHES file-based (OK for dev). No SECURE_* headers config for prod. Risk: Medium.

## Summary of critical gaps (High)

- Multi-tenant enforcement across models/querysets.
- RBAC integration with DRF.
- Universal AuditEvent signals including auth.
- Test coverage for critical modules.
