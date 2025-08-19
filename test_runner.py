#!/usr/bin/env python
"""
Simple test runner for the Book Platform project.
Usage:
    python test_runner.py                    # Run all tests
    python test_runner.py main              # Run tests for main app
    python test_runner.py --coverage        # Run with coverage
    python test_runner.py --fast            # Run with optimized settings
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def run_tests(app=None, coverage=False, fast=False, verbosity=2):
    """Run Django tests with specified options"""
    
    # Set up Django settings
    if fast:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_platform.test_settings')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_platform.settings')
    
    # Build command
    python_path = sys.executable  # Use the current Python interpreter
    if coverage:
        cmd = ['coverage', 'run', '--source=.', 'manage.py', 'test']
    else:
        cmd = [python_path, 'manage.py', 'test']
    
    # Add app if specified
    if app:
        cmd.append(app)
    
    # Add verbosity
    cmd.extend(['--verbosity', str(verbosity)])
    
    # Add parallel testing for faster execution
    if fast:
        cmd.extend(['--parallel', 'auto'])
    
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 50)
    
    # Run the command
    try:
        result = subprocess.run(cmd, check=False)
        
        # If coverage was used, generate report
        if coverage and result.returncode == 0:
            print("\nGenerating coverage report...")
            subprocess.run(['coverage', 'html'])
            subprocess.run(['coverage', 'report'])
            print("Coverage report generated in htmlcov/")
        
        return result.returncode == 0
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure you have Django and coverage installed")
        return False
    except KeyboardInterrupt:
        print("\nTest run interrupted")
        return False

def main():
    parser = argparse.ArgumentParser(description="Book Platform Test Runner")
    parser.add_argument('app', nargs='?', help='Specific app to test (main, accounts, author, news, travel)')
    parser.add_argument('--coverage', '-c', action='store_true', help='Run with coverage report')
    parser.add_argument('--fast', '-f', action='store_true', help='Use optimized test settings')
    parser.add_argument('--quiet', '-q', action='store_true', help='Minimal output')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Set verbosity
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 3
    else:
        verbosity = 2
    
    # Validate app name if provided
    valid_apps = ['main', 'accounts', 'author', 'news', 'travel']
    if args.app and args.app not in valid_apps:
        print(f"Error: Invalid app '{args.app}'. Valid apps: {', '.join(valid_apps)}")
        return 1
    
    print("Book Platform Test Runner")
    print("=" * 50)
    
    if args.app:
        print(f"Testing app: {args.app}")
    else:
        print("Testing all apps")
    
    if args.coverage:
        print("Coverage reporting: enabled")
    
    if args.fast:
        print("Fast mode: enabled (using test settings)")
    
    print()
    
    success = run_tests(
        app=args.app,
        coverage=args.coverage,
        fast=args.fast,
        verbosity=verbosity
    )
    
    if success:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
