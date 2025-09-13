# Shim package to expose inner project config
from importlib import import_module as _im
_inner = _im('FinAsis.config')  # noqa: F401
