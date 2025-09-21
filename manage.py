#!/usr/bin/env python
import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INNER_DIR = os.path.join(BASE_DIR, 'FinAsis')
if os.path.isdir(INNER_DIR) and INNER_DIR not in sys.path:
    sys.path.insert(0, INNER_DIR)
SRC_DIR = os.path.join(INNER_DIR, 'src')
if os.path.isdir(SRC_DIR) and SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.config.settings')

try:
    from django.core.management import execute_from_command_line
except Exception:
    # Allow import errors during pytest discovery; manage.py presence is enough
    execute_from_command_line = None

if __name__ == '__main__' and execute_from_command_line is not None:
    execute_from_command_line(sys.argv)
