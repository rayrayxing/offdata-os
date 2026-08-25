#!/usr/bin/env python3
import unittest,sys
from pathlib import Path
suite=unittest.defaultTestLoader.discover(str(Path(__file__).parent),pattern='test_*.py');r=unittest.TextTestRunner(verbosity=2).run(suite);sys.exit(0 if r.wasSuccessful() else 1)
