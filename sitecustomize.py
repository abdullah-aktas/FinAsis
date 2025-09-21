import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INNER_DIR = os.path.join(BASE_DIR, 'FinAsis')
if os.path.isdir(INNER_DIR) and INNER_DIR not in sys.path:
    sys.path.insert(0, INNER_DIR)
SRC_DIR = os.path.join(INNER_DIR, 'src')
if os.path.isdir(SRC_DIR) and SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
