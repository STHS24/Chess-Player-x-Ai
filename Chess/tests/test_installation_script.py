#!/usr/bin/env python3
"""
Unit tests for the installation verification script.
Tests the functionality of the test_installation.py module.
"""

import unittest
import sys
import os
import io
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the test_installation module
import test_installation

class TestInstallationScript(unittest.TestCase):
    """Test cases for the installation verification script."""

    def test_check_module_installed(self):
        """Test checking for installed modules."""
        # Test with an installed module
        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_module.__version__ = '1.0.0'
            mock_import.return_value = mock_module

            installed, version = test_installation.check_module('installed_module')
            self.assertTrue(installed)
            self.assertEqual(version, '1.0.0')

    def test_check_module_not_installed(self):
        """Test checking for modules that are not installed."""
        # Test with a module that's not installed
        with patch('importlib.import_module', side_effect=ImportError):
            installed, version = test_installation.check_module('not_installed_module')
            self.assertFalse(installed)
            self.assertIsNone(version)

    def test_main_success(self):
        """Test main function with all tests passing."""
        # Mock all the necessary functions and checks to simulate a successful test
        with patch('test_installation.check_module', return_value=(True, '1.0.0')), \
             patch('builtins.open', MagicMock(return_value=MagicMock())), \
             patch('importlib.import_module') as mock_import, \
             patch('test_installation.SunfishWrapper') as mock_wrapper:

            # Mock the import_module to return a module with SunfishWrapper
            mock_module = MagicMock()
            mock_module.SunfishWrapper = mock_wrapper
            mock_import.return_value = mock_module

            # Mock the SunfishWrapper instance
            mock_engine = MagicMock()
            mock_engine.is_initialized = True
            mock_wrapper.return_value = mock_engine

            # Redirect stdout to capture the output
            captured_output = io.StringIO()
            sys.stdout = captured_output

            # Run the main function
            result = test_installation.main()

            # Check the result
            self.assertEqual(result, 0)  # Should return 0 for success

            # Check the output
            output = captured_output.getvalue()
            self.assertIn("All tests passed!", output)

        # Reset stdout
        sys.stdout = sys.__stdout__

    def test_main_failure(self):
        """Test main function with some tests failing."""
        # Mock the check_module function to simulate a missing module
        def mock_check_module(module_name):
            if module_name == 'pygame':
                return True, '1.0.0'
            else:
                return False, None

        with patch('test_installation.check_module', side_effect=mock_check_module), \
             patch('builtins.open', side_effect=FileNotFoundError), \
             patch('importlib.import_module') as mock_import:

            # Mock the import_module to raise an ImportError
            mock_import.side_effect = ImportError("Test error")

            # Redirect stdout to capture the output
            captured_output = io.StringIO()
            sys.stdout = captured_output

            # Run the main function
            result = test_installation.main()

            # Check the result
            self.assertEqual(result, 1)  # Should return 1 for failure

            # Check the output
            output = captured_output.getvalue()
            self.assertIn("Some tests failed", output)

        # Reset stdout
        sys.stdout = sys.__stdout__

if __name__ == "__main__":
    unittest.main()
