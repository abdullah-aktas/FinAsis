# Test Coverage Plan and Status

Target: >= 80% unit test coverage on critical modules.

Initial baseline
- Existing tests focus on UI crawl/accessibility. Minimal domain unit tests found.

Planned tests
- AuditEvent: CRUD + auth event capture, meta enrichment, diffs
- Blockchain anchor: normalization determinism, hashing, verify endpoint
- RBAC permissions: allow/deny per role
- Reports: trial balance and income statement correctness with tenant/date filters

Gaps after PR-1..PR-5
- e-Fatura/e-Defter integration stubs
- Async queue behaviors when Celery introduced

Status: to be updated after running `pytest --cov` once tests added.
