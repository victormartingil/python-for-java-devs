"""Make the module's example code importable from tests.

Module directories (01-python-essentials etc.) are not Python packages
(names start with digits), so tests add the module dir to sys.path here.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
