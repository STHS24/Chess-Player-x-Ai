#!/usr/bin/env python3
"""
Test runner for the Chess AI project.
Runs all the unit tests and integration tests.
"""

import unittest
import sys
import os
import time

def run_tests():
    """Run all tests in the tests directory."""
    # Create the tests directory if it doesn't exist
    if not os.path.exists('tests'):
        os.makedirs('tests')
        print("Created tests directory")
    
    # Create an empty __init__.py file in the tests directory if it doesn't exist
    init_file = os.path.join('tests', '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write("# This file is required to make Python treat the directory as a package\n")
        print("Created tests/__init__.py")
    
    # Discover and run all tests
    start_time = time.time()
    
    print("=" * 70)
    print("Running Chess AI Tests")
    print("=" * 70)
    
    # Discover all tests in the tests directory
    loader = unittest.TestLoader()
    test_suite = loader.discover('tests')
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Print summary
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"Test Summary: {result.testsRun} tests run in {elapsed_time:.2f} seconds")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())
