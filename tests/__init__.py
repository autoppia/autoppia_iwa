import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Only import if the module exists
try:
    from tests.test_di_container import TestDIContainer

    test_container = TestDIContainer()
except ImportError:
    # Skip if test_di_container doesn't exist or has import issues
    test_container = None
