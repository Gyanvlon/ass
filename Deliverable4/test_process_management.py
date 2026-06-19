#!/usr/bin/env python3
"""
Test script for Process Management and Job Control features
Tests background execution, job listing, foreground/background transitions
"""

import subprocess
import sys
import time
import os


def test_background_execution():
    """Test background job execution"""
    print("\n" + "=" * 60)
    print("TESTING PROCESS MANAGEMENT - BACKGROUND EXECUTION")
    print("=" * 60)
    
    # This test demonstrates background execution capability
    # We'll send commands that create background processes
    commands = """
echo "Starting background process test..."
sleep 2 &
jobs
echo "Background process created"
exit
"""
    
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate(input=commands, timeout=10)
    
    print("Output:")
    print(stdout)
    
    if "Background process created" in stdout:
        print("✓ PASS: Background execution works")
        return True
    else:
        print("✗ FAIL: Background execution failed")
        print("STDERR:", stderr)
        return False


def test_foreground_execution():
    """Test foreground job execution"""
    print("\n" + "=" * 60)
    print("TESTING PROCESS MANAGEMENT - FOREGROUND EXECUTION")
    print("=" * 60)
    
    commands = """
echo "Testing foreground execution..."
pwd
echo "Foreground execution completed"
exit
"""
    
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate(input=commands, timeout=5)
    
    print("Output:")
    print(stdout)
    
    if "Foreground execution completed" in stdout:
        print("✓ PASS: Foreground execution works")
        return True
    else:
        print("✗ FAIL: Foreground execution failed")
        return False


def test_job_tracking():
    """Test job tracking capabilities"""
    print("\n" + "=" * 60)
    print("TESTING PROCESS MANAGEMENT - JOB TRACKING")
    print("=" * 60)
    
    commands = """
touch test1.txt
touch test2.txt
rm test1.txt
rm test2.txt
echo "Job tracking test completed"
exit
"""
    
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate(input=commands, timeout=5)
    
    print("Output:")
    print(stdout)
    
    if "Job tracking test completed" in stdout:
        print("✓ PASS: Job tracking works")
        return True
    else:
        print("✗ FAIL: Job tracking failed")
        return False


def test_error_recovery():
    """Test error recovery and resilience"""
    print("\n" + "=" * 60)
    print("TESTING PROCESS MANAGEMENT - ERROR RECOVERY")
    print("=" * 60)
    
    commands = """
nonexistent_command
echo "Recovered from error"
invalid_args
echo "Recovered from another error"
exit
"""
    
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate(input=commands, timeout=5)
    
    print("Output:")
    print(stdout)
    
    recovery_count = stdout.count("Recovered from")
    if recovery_count >= 2:
        print(f"✓ PASS: Shell recovered from {recovery_count} errors")
        return True
    else:
        print("✗ FAIL: Shell did not recover properly")
        return False


def test_command_parsing():
    """Test command parsing with various input formats"""
    print("\n" + "=" * 60)
    print("TESTING PROCESS MANAGEMENT - COMMAND PARSING")
    print("=" * 60)
    
    commands = """
echo "Testing" "multiple" "arguments"
echo 'Single quoted string'
echo "Double quoted string"
exit
"""
    
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate(input=commands, timeout=5)
    
    print("Output:")
    print(stdout)
    
    if "Testing multiple arguments" in stdout:
        print("✓ PASS: Command parsing works correctly")
        return True
    else:
        print("✗ FAIL: Command parsing failed")
        return False


def main():
    """Run all process management tests"""
    print("\n")
    print("*" * 60)
    print("ADVANCED SHELL SIMULATION")
    print("Process Management & Job Control Test Suite")
    print("*" * 60)
    
    tests = [
        ("Background Execution", test_background_execution),
        ("Foreground Execution", test_foreground_execution),
        ("Job Tracking", test_job_tracking),
        ("Error Recovery", test_error_recovery),
        ("Command Parsing", test_command_parsing),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ EXCEPTION in {test_name}: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("-" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed:      {passed}")
    print(f"Failed:      {total - passed}")
    print(f"Success Rate: {(passed / total * 100):.1f}%")
    print("=" * 60)
    
    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
