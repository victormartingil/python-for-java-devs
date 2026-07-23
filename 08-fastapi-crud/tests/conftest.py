"""Put the module root on sys.path so `import tasks_app` works.

Module dirs start with digits (`08-...`), so they can't be Python packages;
conftest.py wires the path instead. Same pattern as module 07's src/ layout.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
