#!/bin/bash
# Setup script for Linux/macOS
# This script sets up the Python environment and installs dependencies

set -e  # Exit on error

echo "==================================="
echo "Security Audit Environment Setup"
echo "==================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "[INFO] Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv
else
    echo "[INFO] Virtual environment already exists."
fi

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "[INFO] Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install requirements
echo "[INFO] Installing requirements..."
pip install -r requirements.txt

# Create logs directory
if [ ! -d "logs" ]; then
    echo "[INFO] Creating logs directory..."
    mkdir -p logs
fi

# Create configs directory
if [ ! -d "configs" ]; then
    echo "[INFO] Creating configs directory..."
    mkdir -p configs
fi

echo ""
echo "==================================="
echo "Setup completed successfully!"
echo "==================================="
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run tests, execute:"
echo "  ./run_test.sh"
echo ""
echo "To run automatic tests with environment detection:"
echo "  python3 auto_test.py"
