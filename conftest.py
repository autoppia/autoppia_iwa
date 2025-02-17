import sys
from pathlib import Path

import pytest

src_path = Path(__file__).resolve().parent

test_src_path = str(src_path / "tests")
project_path = str(src_path / "autoppia_iwa")

if test_src_path not in sys.path:
    sys.path.insert(0, test_src_path)
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Debugging
print("\n==== sys.path Debugging ====")
for path in sys.path:
    print(path)
print("===========================\n")

from autoppia_iwa.src.bootstrap import AppBootstrap
from tests.test_di_container import TestDIContainer


@pytest.fixture(scope="session")
def configured_di_container():
    """
    A global fixture that configures the TestDIContainer for dependency injection.
    """
    container = TestDIContainer()
    AppBootstrap()

    yield container
