#!/usr/bin/env python
"""
Setup script to prepare the test environment.
"""
import subprocess
import sys
import os

def run(cmd):
    """Run a command and print output."""
    print(f"\n{'='*60}")
    print(f"Running: {cmd}")
    print('='*60)
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Error: command failed with code {result.returncode}")
        sys.exit(1)

os.chdir(os.path.dirname(__file__))

# Install dependencies
run(f"{sys.executable} -m pip install -q -r requirements.txt")

print("\n" + "="*60)
print("Test environment ready!")
print("="*60)
print("\nRun tests with:")
print("  python -m pytest tests/ -v")
print("\nRun with coverage:")
print("  python -m pytest tests/ -v --cov=. --cov-report=html")
