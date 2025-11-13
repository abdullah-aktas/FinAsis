#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
from __future__ import annotations

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def main() -> None:
    """Run administrative tasks."""
    sys.path.insert(0, str(BASE_DIR))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line  # type: ignore
    except ImportError as exc:  # pragma: no cover - informs user about setup
        raise ImportError(
            "Django import edilemedi. Sanal ortamınızın ve bağımlılıkların "
            "yüklü olduğundan emin olun."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

