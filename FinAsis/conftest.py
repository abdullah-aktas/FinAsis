import sys
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

# Add inner project directory so `src` package is importable from repository root as well
INNER_DIR = os.path.join(BASE_DIR, 'FinAsis')
if os.path.isdir(INNER_DIR) and INNER_DIR not in sys.path:
	sys.path.insert(0, INNER_DIR)