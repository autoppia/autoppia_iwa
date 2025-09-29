"""
Test package for task generation components.

This package contains comprehensive unit tests for:
- TaskGenerationPipeline
- GlobalTaskGenerationPipeline
- Test generation pipelines
- Task caching and serialization
- Configuration validation
- Prompt templates
"""

import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

__version__ = "1.0.0"
