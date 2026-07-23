"""Put the src/ layout package on sys.path for tests.

In a packaged project you'd `uv pip install -e .` instead; this repo keeps
module 07 self-contained, so conftest.py wires the path.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
