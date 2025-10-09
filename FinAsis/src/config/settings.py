"""
Environment selecting shim for settings.

Public import path remains 'src.config.settings'. This module imports the
appropriate environment module from settings_pkg based on DJANGO_ENV.
Fallback: base settings.
"""
import os as _os
from importlib import import_module as _import_module

_DJANGO_ENV = _os.environ.get('DJANGO_ENV', '').lower().strip()
_MODULE_MAP = {
    'local': 'src.config.settings_pkg.local',
    'test': 'src.config.settings_pkg.test',
    'production': 'src.config.settings_pkg.production',
}
_TARGET = _MODULE_MAP.get(_DJANGO_ENV, 'src.config.settings_pkg.base')
_mod = _import_module(_TARGET)
globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith('_')})

