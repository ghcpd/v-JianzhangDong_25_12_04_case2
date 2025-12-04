#!/bin/bash

# Setup script for Linux/macOS environments
echo "Setting up environment for security audit project..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "Python 3 detected: $(python3 --version)"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p config
mkdir -p logs

# Create sample config file
echo "Creating sample configuration..."
cat > config/sample.yaml << EOF
app:
  name: "Security Audit Test App"
  version: "1.0.0"
settings:
  debug: false
  log_level: "INFO"
EOF

# Set environment variables (for testing only - in production use proper secret management)
echo "Setting up environment variables..."
cat > .env << EOF
PAYMENT_TOKEN=tok_test_123456
MAIL_SERVER_KEY=mail_test_key_XYZ
INTERNAL_AUTH=test_auth_secret_789
ALLOWED_DOMAINS=api.payment-service.com,localhost
EOF

echo ""
echo "Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To set environment variables, run:"
echo "  source .env  # or export the variables manually"
echo ""
echo "To run the tests, execute:"
echo "  ./run_test.sh"
echo ""
