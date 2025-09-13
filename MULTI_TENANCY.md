# Multi‑Tenancy & RBAC Plan (MVP → Scale)

This document outlines a pragmatic path to multi‑tenant isolation and role-based access control in FinAsis.

## Goals
- Single deployment, many tenants (companies/schools).
- Strong data isolation; safe by default.
- Low friction migrations from MVP to advanced modes.

## Terminology
- Tenant: the owning organization (school, SME, partner).
- Company: legal entity within a tenant (may be 1..N per tenant).

## Approach

Phase 1 (MVP) – Row‑level tenancy
- Add models:
  - Tenant(id, name, subdomain, is_active)
  - Company(…, tenant FK)
  - UserTenant (user FK, tenant FK, roles: owner/admin/member)
- Middleware: resolve current tenant via subdomain/header; attach to request.tenant.
- Query filters: managers/mixins that auto‑filter by request.tenant.
- Caching: include tenant key in cache prefix.
- Storage: Media path prefix per tenant (e.g., media/<tenant_id>/…).
- DRF: Permission classes ensure object.tenant == request.tenant.

Phase 2 – Schema per tenant (optional)
- Introduce `django-tenants` or `django-multitenant` for Postgres schemas.
- Use a bridge model to map host → schema.
- Migrations: per‑tenant operations.

Phase 3 – Cross‑tenant services
- Aggregated analytics in ClickHouse; CDC streaming from OLTP.
- Async tasks scoped by tenant (Celery routing keys).

## RBAC
- Keep existing Role/Permission models (FinAsis.apps.permissions).
- Scope: role assignments per (tenant, company, user).
- DRF permissions: object‑level check on tenant/company and action (create/read/update/delete/export).

## Backwards compatible scaffolding
- Do NOT break current models. Introduce nullable tenant/company FK fields with data migration defaulting to a “public” tenant.
- Provide SafeManager mixin to apply tenant filter only in request context.

## Milestones
1) Domain model additions + middleware + safe managers.
2) Wire DRF base viewsets to enforce tenant scoping.
3) Migrate critical apps (accounts, accounting, finance) to include tenant/company FKs.
4) Add per‑tenant cache/media prefixes.
5) Optional: adopt django-tenants for schema isolation at scale.
