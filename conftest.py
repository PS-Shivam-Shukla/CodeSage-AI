"""
conftest.py
===========

Root pytest configuration file.

Adds the project root directory to sys.path so all ``app.*``
imports resolve correctly when running tests from any working directory.

This is the standard pattern for Python projects that do NOT use
an editable install (pip install -e .).
"""

import sys
from pathlib import Path

# Insert the project root (directory containing this file) at the front
# of sys.path so ``from app.evaluation import ...`` works in all tests.
sys.path.insert(0, str(Path(__file__).parent))
