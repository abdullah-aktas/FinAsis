"""Settings package.

Environment-specific modules live here:
- base.py
- local.py
- test.py
- production.py

Use src.config.settings (module) as the public import path; it selects one of
these modules at runtime based on DJANGO_ENV. This package itself doesn't load
anything by default to avoid surprises during static analysis.
"""
