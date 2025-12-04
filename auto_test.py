#!/usr/bin/env python3
"""
Automatic test execution script with environment detection.

This script:
- Detects the current environment (Windows/Linux/Docker)
- Runs the corresponding test script
- Saves output logs to logs/test_run.log
- Includes timestamp and final status (TEST PASSED or TEST FAILED)
"""

import os
import sys
import subprocess
import platform
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "test_run.log"

# Setup logging with both file and console output
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def detect_environment():
    """Detect the current operating system and environment."""
    system = platform.system()
    
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "macos"
    elif system == "Linux":
        # Check if running in Docker
        if Path("/.dockerenv").exists():
            return "docker"
        return "linux"
    else:
        return "unknown"


def run_tests_windows():
    """Run tests on Windows using run_test.bat."""
    logger.info("Detected environment: Windows")
    logger.info("Running test script: run_test.bat")
    logger.info("=" * 70)
    
    try:
        result = subprocess.run(
            ["cmd.exe", "/c", "run_test.bat"],
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        # Log output
        if result.stdout:
            for line in result.stdout.split('\n'):
                if line.strip():
                    logger.info(line)
        
        if result.stderr:
            for line in result.stderr.split('\n'):
                if line.strip():
                    logger.warning(line)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        logger.error("Test execution timed out after 300 seconds")
        return False
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        return False


def run_tests_unix():
    """Run tests on Linux/macOS using run_test.sh."""
    env = detect_environment()
    if env == "macos":
        logger.info("Detected environment: macOS")
    elif env == "docker":
        logger.info("Detected environment: Docker (Linux)")
    else:
        logger.info("Detected environment: Linux")
    
    logger.info("Running test script: run_test.sh")
    logger.info("=" * 70)
    
    try:
        # Make script executable
        script_path = Path("run_test.sh")
        if script_path.exists():
            script_path.chmod(0o755)
        
        result = subprocess.run(
            ["bash", "run_test.sh"],
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        # Log output
        if result.stdout:
            for line in result.stdout.split('\n'):
                if line.strip():
                    logger.info(line)
        
        if result.stderr:
            for line in result.stderr.split('\n'):
                if line.strip():
                    logger.warning(line)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        logger.error("Test execution timed out after 300 seconds")
        return False
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        return False


def main():
    """Main entry point."""
    logger.info("=" * 70)
    logger.info("SECURITY AUDIT TEST SUITE")
    logger.info("=" * 70)
    
    # Detect environment
    env = detect_environment()
    
    # Run appropriate test script
    success = False
    if env == "windows":
        success = run_tests_windows()
    elif env in ["linux", "macos", "docker"]:
        success = run_tests_unix()
    else:
        logger.error(f"Unknown environment: {env}")
        logger.error("Cannot determine which test script to run")
        success = False
    
    # Log final status
    logger.info("=" * 70)
    if success:
        logger.info("TEST PASSED")
        logger.info("All security fixes have been validated successfully.")
        return 0
    else:
        logger.error("TEST FAILED")
        logger.error("Some tests did not pass. Please review the logs above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
