#!/usr/bin/env python3
"""
Auto Test Script - Automatic Environment Detection and Testing
This script detects the current environment and runs the appropriate test script.
Logs are saved to logs/test_run.log with timestamps and status.
"""

import os
import sys
import platform
import subprocess
from datetime import datetime
import shutil


def ensure_logs_directory():
    """Create logs directory if it doesn't exist"""
    if not os.path.exists("logs"):
        os.makedirs("logs")
        print("Created logs directory")


def get_timestamp():
    """Get current timestamp in ISO format"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def detect_environment():
    """
    Detect the current operating environment
    Returns: 'windows', 'linux', 'darwin' (macOS), or 'docker'
    """
    # Check if running in Docker
    if os.path.exists("/.dockerenv") or os.path.exists("/run/.containerenv"):
        return "docker"
    
    # Check OS platform
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    elif system == "darwin":
        return "darwin"  # macOS
    else:
        return "unknown"


def run_test_script(script_path, shell=False):
    """
    Run a test script and capture output
    Returns: (return_code, output)
    """
    try:
        print(f"Executing: {script_path}")
        result = subprocess.run(
            script_path if isinstance(script_path, list) else [script_path],
            shell=shell,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return -1, "ERROR: Test script timed out after 300 seconds"
    except Exception as e:
        return -1, f"ERROR: Failed to run test script: {str(e)}"


def log_test_results(log_file, test_name, output, return_code):
    """Log test results to file with timestamp"""
    timestamp = get_timestamp()
    status = "TEST PASSED" if return_code == 0 else "TEST FAILED"
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write(f"Test: {test_name}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Return Code: {return_code}\n")
        f.write("=" * 80 + "\n")
        f.write(output)
        f.write("\n")
        f.write("-" * 80 + "\n")
        f.write(f"Status: {status}\n")
        f.write("=" * 80 + "\n\n")


def test_file(file_name, env):
    """
    Test a specific Python file by temporarily renaming it to inputs.py
    Returns: (return_code, output)
    """
    original_inputs = "inputs.py"
    temp_backup = "inputs_temp_backup.py"
    
    # If testing inputs.py itself, no need to swap files
    if file_name == original_inputs:
        # Run tests directly on inputs.py
        if env == "windows":
            return_code, output = run_test_script("run_test.bat", shell=True)
        else:  # linux, darwin, docker
            # Make script executable
            os.chmod("run_test.sh", 0o755)
            return_code, output = run_test_script(["bash", "run_test.sh"])
        return return_code, output
    
    # For other files (like inputs_backup.py), swap temporarily
    # Backup original inputs.py if it exists
    if os.path.exists(original_inputs):
        shutil.copy(original_inputs, temp_backup)
    
    # Copy test file to inputs.py
    shutil.copy(file_name, original_inputs)
    
    try:
        # Run the appropriate test script
        if env == "windows":
            return_code, output = run_test_script("run_test.bat", shell=True)
        else:  # linux, darwin, docker
            # Make script executable
            os.chmod("run_test.sh", 0o755)
            return_code, output = run_test_script(["bash", "run_test.sh"])
        
        return return_code, output
    finally:
        # Restore original inputs.py
        if os.path.exists(temp_backup):
            shutil.copy(temp_backup, original_inputs)
            os.remove(temp_backup)
        else:
            # If there was no original, restore from the backup we should have
            if os.path.exists("inputs_backup.py") and file_name == "inputs_backup.py":
                # Don't delete inputs.py in this case
                pass


def main():
    """Main execution function"""
    print("=" * 80)
    print("Auto Test Script - Security Audit Testing")
    print("=" * 80)
    print()
    
    # Ensure logs directory exists
    ensure_logs_directory()
    log_file = "logs/test_run.log"
    
    # Clear previous log
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # Detect environment
    env = detect_environment()
    print(f"Detected environment: {env}")
    print(f"Platform: {platform.platform()}")
    print(f"Python version: {platform.python_version()}")
    print()
    
    # Write header to log file
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("SECURITY AUDIT TEST RUN LOG\n")
        f.write("=" * 80 + "\n")
        f.write(f"Start Time: {get_timestamp()}\n")
        f.write(f"Environment: {env}\n")
        f.write(f"Platform: {platform.platform()}\n")
        f.write(f"Python Version: {platform.python_version()}\n")
        f.write("=" * 80 + "\n\n")
    
    if env == "unknown":
        error_msg = "ERROR: Unknown environment detected. Cannot proceed with tests."
        print(error_msg)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(error_msg + "\n")
            f.write("Status: TEST FAILED\n")
        sys.exit(1)
    
    # Check if test scripts exist
    test_script = "run_test.bat" if env == "windows" else "run_test.sh"
    if not os.path.exists(test_script):
        error_msg = f"ERROR: Test script '{test_script}' not found!"
        print(error_msg)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(error_msg + "\n")
            f.write("Status: TEST FAILED\n")
        sys.exit(1)
    
    # Test both files
    all_passed = True
    
    # Test 1: inputs_backup.py (should show vulnerabilities)
    print("\n" + "=" * 80)
    print("TEST 1: Testing inputs_backup.py (vulnerable version)")
    print("=" * 80)
    
    if os.path.exists("inputs_backup.py"):
        return_code, output = test_file("inputs_backup.py", env)
        print(output)
        log_test_results(log_file, "inputs_backup.py", output, return_code)
        
        # For backup file, we expect it to fail security tests
        # So we just log the results without changing all_passed
        print(f"\nTest completed for inputs_backup.py with return code: {return_code}")
    else:
        error_msg = "ERROR: inputs_backup.py not found!"
        print(error_msg)
        log_test_results(log_file, "inputs_backup.py", error_msg, -1)
    
    # Test 2: inputs.py (should pass security tests)
    print("\n" + "=" * 80)
    print("TEST 2: Testing inputs.py (secured version)")
    print("=" * 80)
    
    if os.path.exists("inputs.py"):
        return_code, output = test_file("inputs.py", env)
        print(output)
        log_test_results(log_file, "inputs.py", output, return_code)
        
        if return_code != 0:
            all_passed = False
        
        print(f"\nTest completed for inputs.py with return code: {return_code}")
    else:
        error_msg = "ERROR: inputs.py not found!"
        print(error_msg)
        log_test_results(log_file, "inputs.py", error_msg, -1)
        all_passed = False
    
    # Write final summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write("\n" + "=" * 80 + "\n")
        f.write("FINAL TEST SUMMARY\n")
        f.write("=" * 80 + "\n")
        f.write(f"End Time: {get_timestamp()}\n")
        
        if all_passed:
            final_status = "TEST PASSED"
            print("All security tests PASSED!")
            print(f"Results logged to: {log_file}")
            f.write("All security tests PASSED!\n")
        else:
            final_status = "TEST FAILED"
            print("Some security tests FAILED!")
            print(f"Results logged to: {log_file}")
            f.write("Some security tests FAILED!\n")
        
        f.write(f"Final Status: {final_status}\n")
        f.write("=" * 80 + "\n")
    
    print(f"Final Status: {final_status}")
    print("=" * 80)
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
