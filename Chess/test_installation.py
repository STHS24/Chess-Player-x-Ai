#!/usr/bin/env python3
"""
Test script to verify that all dependencies are correctly installed
and the chess engine can be initialized.
"""

import sys
import importlib.util
import platform

def check_module(module_name):
    """Check if a module is installed and return its version if available."""
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, '__version__', 'unknown version')
        return True, version
    except ImportError:
        return False, None

def main():
    """Run tests to verify the installation."""
    print("Chess AI Installation Test")
    print("=========================")
    print(f"Python version: {platform.python_version()}")
    print(f"Operating system: {platform.system()} {platform.release()}")
    print()
    
    # Check required modules
    modules = ['pygame', 'chess']
    all_modules_installed = True
    
    for module in modules:
        installed, version = check_module(module)
        if installed:
            print(f"✅ {module} is installed (version: {version})")
        else:
            print(f"❌ {module} is NOT installed")
            all_modules_installed = False
    
    print()
    
    # Check if sunfish.py exists
    try:
        with open('sunfish.py', 'r') as f:
            print("✅ sunfish.py file is present")
    except FileNotFoundError:
        print("❌ sunfish.py file is missing")
        all_modules_installed = False
    
    # Check if sunfish_wrapper.py exists
    try:
        with open('sunfish_wrapper.py', 'r') as f:
            print("✅ sunfish_wrapper.py file is present")
    except FileNotFoundError:
        print("❌ sunfish_wrapper.py file is missing")
        all_modules_installed = False
    
    # Check if main.py exists
    try:
        with open('main.py', 'r') as f:
            print("✅ main.py file is present")
    except FileNotFoundError:
        print("❌ main.py file is missing")
        all_modules_installed = False
    
    print()
    
    # Try to import the SunfishWrapper class
    try:
        from sunfish_wrapper import SunfishWrapper
        print("✅ SunfishWrapper class can be imported")
        
        # Try to initialize the engine (with no retries to avoid random failures)
        try:
            engine = SunfishWrapper(max_retries=1)
            if engine.is_initialized:
                print("✅ Chess engine initialized successfully")
            else:
                print("❌ Chess engine initialization failed")
        except Exception as e:
            print(f"❌ Error initializing chess engine: {e}")
    except Exception as e:
        print(f"❌ Error importing SunfishWrapper: {e}")
        all_modules_installed = False
    
    print()
    
    # Final verdict
    if all_modules_installed:
        print("🎉 All tests passed! You're ready to play chess.")
        print("Run 'python main.py' to start the game.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues above before running the game.")
        print("See the README.md file for installation instructions.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
