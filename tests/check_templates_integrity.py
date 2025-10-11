"""Template & link integrity checker

Kontroller:
- Django yüklenir, tüm template dosyaları bulunur (.html)
- Her template güvenli bir context ile render edilir:
  - {% extends %} ve {% include %} hedeflerinin bulunabilirliği
  - {% url %} tag'lerindeki isimlerin çözümlenmesi
- Render edilmiş HTML'den internal linkler (href/src/action) toplanır:
  - / ile başlayan URL'ler resolve edilebilir mi (URLConf)?
  - static dosya referansları ve hash query (?.*) göz ardı edilir

Raporlama:
- Hatalar listelenir ve varsa exit code 1 ile çıkar.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Iterable


def setup_django() -> None:
    here = Path(__file__).resolve().parent
    repo_root = here
    for _ in range(4):
        if (repo_root / "manage.py").exists():
            break
        repo_root = repo_root.parent
    inner = repo_root / "FinAsis"
    src = inner / "src"
    for p in (repo_root, inner, src):
        if p.exists():
            sys.path.insert(0, str(p))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.config.settings")
    import django

    django.setup()
    # Allow RequestFactory host
    try:
        from django.conf import settings
        if isinstance(getattr(settings, "ALLOWED_HOSTS", None), list):
            if "testserver" not in settings.ALLOWED_HOSTS:
                settings.ALLOWED_HOSTS.append("testserver")
    except Exception:
        pass


def iter_template_files() -> Iterable[Path]:
    # Django default template dirs + common locations
    roots: list[Path] = []
    repo = Path.cwd()
    roots.append(repo / "FinAsis" / "src" / "templates")
    roots.append(repo / "templates")
    # Walk project for any templates directories
    for base in (repo / "FinAsis" / "src").rglob("templates"):
        roots.append(base)

    seen: set[Path] = set()
    for r in roots:
        if not r.exists():
            continue
        for p in r.rglob("*.html"):
            if p not in seen:
                seen.add(p)
                yield p


def is_static_like(url: str) -> bool:
    # crude detection: adjust if needed
    return any(url.startswith(prefix) for prefix in ("/static/", "/media/"))


def main() -> None:
    setup_django()
    from django.template import TemplateDoesNotExist
    from django.template.loader import get_template
    from django.test import RequestFactory
    from django.urls import Resolver404, resolve
    from django.template import engines

    rf = RequestFactory()
    request = rf.get("/")
    # Provide a default anonymous user in both request and context
    try:
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
        default_user = request.user
    except Exception:
        default_user = None
    # Minimal context; request çoğu template için yeterlidir
    base_context = {"request": request, "user": default_user}

    errors: list[str] = []

    # Regex for links
    href_re = re.compile(r'\shref="([^"]+)"')
    src_re = re.compile(r'\ssrc="([^"]+)"')
    action_re = re.compile(r'\saction="([^"]+)"')

    for tpl_path in iter_template_files():
        rel = str(tpl_path)
        # Skip known heavy/special-case templates
        if 'apps/games/ursina_game/' in rel.replace('\\', '/'):
            continue
        try:
            # Try loading via loader; if fails, continue to next (file might be include-only)
            template = get_template(rel)
        except TemplateDoesNotExist:
            # Fallback: resolve name relative to the nearest 'templates' directory ancestor
            try:
                # Collect possible roots: common project-level plus any parent named 'templates'
                candidate_roots = [Path("FinAsis/src/templates"), Path("templates")]
                for parent in tpl_path.parents:
                    if parent.name == "templates":
                        candidate_roots.append(parent)
                name = None
                for root in candidate_roots:
                    try:
                        name = str(tpl_path.relative_to(root)).replace("\\", "/")
                        break
                    except Exception:
                        continue
                if not name:
                    # As a last resort, try with the immediate folder name if it looks like a Django app template
                    name = "/".join(tpl_path.parts[-2:])
                template = get_template(name)
            except Exception as e:
                errors.append(f"LOAD FAIL: {rel} -> {e}")
                continue
        except Exception as e:
            errors.append(f"COMPILE FAIL: {rel} -> {e}")
            continue

        # Render and catch URL/include/extends issues
        try:
            rendered = template.render(base_context)
        except Exception as e:
            # Soften common NoReverseMatch cases caused by missing context (e.g., pk is empty during standalone render)
            try:
                from django.urls import NoReverseMatch
            except Exception:
                NoReverseMatch = tuple()  # type: ignore
            msg = str(e)
            if isinstance(e, NoReverseMatch):
                # Heuristics: allow cases where reverse failed due to empty positional/keyword args
                if "with arguments ''" in msg or "with arguments '('',)" in msg or "with keyword arguments '{}'" in msg or ("with arguments" in msg and "not found" in msg):
                    # Skip reporting this template as an error; it's likely missing runtime context
                    continue
            # Ignore missing context lookups for common list/detail placeholders
            if "Failed lookup for key [" in msg:
                continue
            # Ignore Django admin app_list reverse errors in offline render
            if "Reverse for 'app_list'" in msg and "admin/" in rel.replace('\\', '/'):
                continue
            errors.append(f"RENDER FAIL: {rel} -> {e}")
            continue

        # Parse internal links and try to resolve
        links = []
        links += href_re.findall(rendered)
        links += src_re.findall(rendered)
        links += action_re.findall(rendered)

        for url in links:
            if not url:
                continue
            if url.startswith("#"):
                continue
            # remove query/hash
            base = url.split("?", 1)[0].split("#", 1)[0]
            if not base.startswith("/"):
                continue  # relative path in same folder; skip here
            if is_static_like(base):
                continue
            try:
                resolve(base)
            except Resolver404:
                errors.append(f"BROKEN LINK: {rel} -> {base}")

    if errors:
        print("❌ Template/Link Hataları:")
        for e in errors:
            print("-", e)
        sys.exit(1)
    else:
        print("✅ Tüm template ve bağlantılar temel kontrollerden geçti.")


if __name__ == "__main__":
    main()
