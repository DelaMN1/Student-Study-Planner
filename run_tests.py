#!/usr/bin/env python3
"""
Test runner script for Student Study Planner
Runs all tests with coverage reporting
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {description}:")
        print(f"Exit code: {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description='Run tests for Student Study Planner')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--frontend', action='store_true', help='Run only frontend tests')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--html', action='store_true', help='Generate HTML coverage report')
    
    args = parser.parse_args()
    
    # Set up environment
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'True'
    
    # Base pytest command
    pytest_cmd = ['python', '-m', 'pytest']
    
    if args.verbose:
        pytest_cmd.append('-v')
    
    if args.coverage:
        pytest_cmd.extend([
            '--cov=.',
            '--cov-report=term-missing',
            '--cov-report=html' if args.html else '--cov-report=term'
        ])
    
    # Determine which tests to run
    if args.unit:
        test_paths = ['tests/test_models.py', 'tests/test_utils.py']
    elif args.integration:
        test_paths = ['tests/test_routes.py']
    elif args.frontend:
        test_paths = ['tests/test_frontend.py']
    else:
        # Run all tests
        test_paths = ['tests/']
    
    pytest_cmd.extend(test_paths)
    
    # Run the tests
    success = run_command(pytest_cmd, "pytest tests")
    
    if success:
        print("\n✅ All tests passed!")
        
        if args.coverage:
            print("\n📊 Coverage report generated!")
            if args.html:
                print("📁 HTML coverage report available in htmlcov/")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == '__main__':
    main() 