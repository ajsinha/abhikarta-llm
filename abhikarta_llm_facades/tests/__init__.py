"""
Tests Module - Abhikarta LLM Facades

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

This module contains unit tests for all provider facades.
"""

import os
import sys
import unittest

# Add parent directory to path to allow imports
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

__version__ = '1.0.0'
__author__ = 'Ashutosh Sinha'
__email__ = 'ajsinha@gmail.com'


def run_all_tests():
    """Run all test suites."""
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.dirname(__file__), pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


if __name__ == '__main__':
    run_all_tests()
