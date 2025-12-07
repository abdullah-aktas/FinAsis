"""
Django yerelleştirme uygulaması. Python standart kütüphanesindeki ``locale``
modülü ile çakışmayı önlemek için burada standart modülü yükleyip tüm
sembollerini yeniden dışa aktarıyoruz.
"""

from __future__ import annotations

import os as _os
from importlib import util as _importlib_util

_stdlib_locale_path = _os.path.join(_os.path.dirname(_os.__file__), "locale.py")
_spec = _importlib_util.spec_from_file_location("_stdlib_locale", _stdlib_locale_path)
if _spec is None or _spec.loader is None:  # pragma: no cover - should not happen
    raise ImportError("Standart locale modülü yüklenemedi")

_stdlib_locale = _importlib_util.module_from_spec(_spec)
_spec.loader.exec_module(_stdlib_locale)

# stdlib locale içindeki sembolleri (fonksiyon, değişken vb.) bu modüle kopyala
for _name in dir(_stdlib_locale):
    if _name in {"__loader__", "__package__", "__spec__"}:
        continue
    globals()[_name] = getattr(_stdlib_locale, _name)

__all__ = getattr(_stdlib_locale, "__all__", [])

del _stdlib_locale, _spec, _stdlib_locale_path, _os, _importlib_util, _name
