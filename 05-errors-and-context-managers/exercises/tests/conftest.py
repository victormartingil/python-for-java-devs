"""Make the exercise stubs importable from tests.

Same pattern as the module's own tests/: exercises/ goes on sys.path
(these directories can't be packages — their names start with digits).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
