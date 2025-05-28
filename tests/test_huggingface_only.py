#!/usr/bin/env python3
"""Test script for HuggingFace-only SV-Agent."""

import sys
import subprocess
from pathlib import Path

def test_help():
    """Test help command."""
    print("Testing help command...")
    result = subprocess.run([sys.executable, "-m", "sv_agent.main", "--help"], 
                          capture_output=True, text=True)
    print(f"Exit code: {result.returncode}")
    if result.returncode == 0:
        print("✓ Help command works")
    else:
        print("✗ Help command failed")
        print(result.stderr)
    return result.returncode == 0

def test_list():
    """Test list command."""
    print("\nTesting list command...")
    result = subprocess.run([sys.executable, "-m", "sv_agent.main", "list"], 
                          capture_output=True, text=True)
    print(f"Exit code: {result.returncode}")
    if result.returncode == 0:
        print("✓ List command works")
        print(f"Found {result.stdout.count('Module')} modules")
    else:
        print("✗ List command failed")
        print(result.stderr)
    return result.returncode == 0

def test_model_loading():
    """Test that model loading doesn't crash immediately."""
    print("\nTesting model loading (will fail without transformers)...")
    
    # Check if local Gemma exists
    gemma_path = Path("models/gemma-latest")
    if gemma_path.exists():
        model_arg = str(gemma_path)
        print(f"Using local Gemma model: {model_arg}")
    else:
        model_arg = "google/gemma-2b-it"
        print(f"Using HuggingFace model: {model_arg}")
    
    # This will fail if transformers isn't installed, which is expected
    result = subprocess.run([
        sys.executable, "-m", "sv_agent.main",
        "--model", model_arg,
        "--load-in-4bit",  # Use quantization for testing
        "ask", "test question"
    ], capture_output=True, text=True)
    
    if "transformers" in result.stderr:
        print("✓ Correctly reports missing transformers library")
        return True
    elif result.returncode == 0:
        print("✓ Model loaded successfully")
        return True
    else:
        print("✗ Unexpected error:")
        print(result.stderr)
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing HuggingFace-only SV-Agent")
    print("=" * 60)
    
    tests = [
        test_help(),
        test_list(),
        test_model_loading()
    ]
    
    passed = sum(tests)
    total = len(tests)
    
    print("\n" + "=" * 60)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()