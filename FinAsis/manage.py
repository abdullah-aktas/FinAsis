#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks.

    This project has a nested structure (FinAsis/FinAsis/FinAsis/config).
    When manage.py is executed from the parent directory (FinAsis/FinAsis),
    the inner package containing the actual `config` module is NOT on sys.path,
    causing `ModuleNotFoundError: config`.

    We defensively insert the inner FinAsis directory (sibling of this file)
    so both invoking locations work (escaped backslashes shown):
        D:\\FinAsis\\FinAsis> python manage.py ...
        D:\\FinAsis\\FinAsis\\FinAsis> python manage.py ...
    """

    current_dir = os.path.dirname(os.path.abspath(__file__))
    inner_project_dir = os.path.join(current_dir, 'FinAsis')
    # If the inner directory exists and not already in sys.path, add it to resolve 'config'
    if os.path.isdir(inner_project_dir) and inner_project_dir not in sys.path:
        sys.path.insert(0, inner_project_dir)

    # Tam paket yolu: FinAsis.config.settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
