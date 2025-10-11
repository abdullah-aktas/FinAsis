"""Generate minimal UI placeholder templates for missing screens.

- Reads required_screens from tests.check_ui_completeness
- Uses its discovery functions to know what's already present
- Creates minimal .html files under FinAsis/src/templates/auto_placeholders/
- Each file is named <screen>.html and contains a simple heading.

Safe to run multiple times.
"""
from pathlib import Path
import importlib
import sys

ROOT = Path(__file__).resolve().parents[1]
# Ensure inner src in path similar to manage.py
inner = ROOT / "FinAsis"
src = inner / "src"
for p in (ROOT, inner, src):
    if p.exists():
        sys.path.insert(0, str(p))

mod = importlib.import_module("tests.check_ui_completeness")
required_screens = list(dict.fromkeys([s.strip().lower() for s in mod.required_screens]))

discover_templates_from_files = getattr(mod, "discover_templates_from_files")
discover_templates_from_urls = getattr(mod, "discover_templates_from_urls")

existing = set(discover_templates_from_files()).union(set(discover_templates_from_urls()))

out_dir = src / "templates" / "auto_placeholders"
out_dir.mkdir(parents=True, exist_ok=True)

created = []
for screen in required_screens:
    if screen in existing:
        continue
    target = out_dir / f"{screen}.html"
    if target.exists():
        continue
    target.write_text(f"""
<!doctype html>
<html lang=\"tr\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{screen}</title>
</head>
<body>
  <main style=\"max-width:960px;margin:2rem auto;font-family:system-ui, sans-serif;\">\n\n    <h1 style=\"font-weight:600\">{screen}</h1>
    <p>Bu sayfa henüz tasarlanmadı. Otomatik yer tutucu.</p>

  </main>
</body>
</html>
""".lstrip(), encoding="utf-8")
    created.append(str(target.relative_to(ROOT)))

if created:
    print("✅ Oluşturulan placeholder dosyalar:")
    for c in created:
        print("-", c)
else:
    print("ℹ️ Oluşturulacak eksik placeholder bulunamadı (ya da hepsi mevcut).")
