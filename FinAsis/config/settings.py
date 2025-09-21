import os
import sys

# Ensure 'src' package inside this project is importable
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, '..'))
if _PROJECT_ROOT not in sys.path:
	sys.path.insert(0, _PROJECT_ROOT)

# Re-export settings from src package for pytest-django
from src.config.settings import *  # type: ignore # noqa

# Ensure URL conf points to src project urls
ROOT_URLCONF = 'src.config.urls'
