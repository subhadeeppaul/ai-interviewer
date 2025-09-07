# tests/conftest.py
import sys, pathlib

# Add project root (the folder containing "src/") to sys.path
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
