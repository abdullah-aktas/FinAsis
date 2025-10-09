import sys
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def _add(p: str):
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

_add(BASE_DIR)

# Support both current nested layout FinAsis/FinAsis/src and future flattened src/
outer = os.path.join(BASE_DIR, 'FinAsis')  # first level
inner = os.path.join(outer, 'FinAsis')     # second level (actual python package root)
candidate_srcs = [
    os.path.join(outer, 'src'),
    os.path.join(inner, 'src'),
    os.path.join(BASE_DIR, 'src'),
]
for p in [outer, inner] + candidate_srcs:
    _add(p)

# Ensure minimal env so importing Django settings in tests doesn't crash
os.environ.setdefault('SECRET_KEY', 'test-secret-key')
os.environ.setdefault('USE_SQLITE', '1')
os.environ.setdefault('DEBUG', '0')

# Normalize DJANGO_SETTINGS_MODULE early so tests need not redefine
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FinAsis.config.settings')
