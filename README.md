# Security Audit Report - Flask Application

## Overview

This repository contains a comprehensive security audit and remediation of a Flask application (`inputs.py`). The audit identified **7 critical security vulnerabilities** that have been fixed in the secured version.

## Project Structure

```
.
├── inputs.py              # Secured version of the application
├── inputs_backup.py       # Original vulnerable version (backup)
├── report.json           # Detailed vulnerability report in JSON format
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker containerization configuration
├── setup.sh             # Setup script for Linux/macOS
├── run_test.sh          # Test script for Linux/macOS
├── run_test.bat         # Test script for Windows
├── auto_test.py         # Automatic test execution script
├── README.md            # This file
├── config/              # Configuration files directory
└── logs/                # Test execution logs directory
    └── test_run.log     # Auto-generated test execution log
```

## Files Description

### Core Files
- **`inputs.py`**: The secured Flask application with all vulnerabilities fixed
- **`inputs_backup.py`**: Original vulnerable version (preserved for comparison)
- **`report.json`**: Structured JSON report containing:
  - Summary of all vulnerabilities (count by severity)
  - Detailed information for each vulnerability
  - Line numbers, severity ratings, descriptions
  - Fix explanations and secure code snippets

### Environment Setup
- **`requirements.txt`**: Python package dependencies (Flask, requests, PyYAML)
- **`Dockerfile`**: Container configuration for Docker deployment
- **`setup.sh`**: Automated environment setup for Linux/macOS systems

### Testing Scripts
- **`run_test.sh`**: Security validation tests for Linux/macOS
- **`run_test.bat`**: Security validation tests for Windows
- **`auto_test.py`**: Cross-platform automatic testing with environment detection

## Vulnerabilities Identified and Fixed

### Critical Severity (3)
1. **Hardcoded Secrets** (Lines 11-13)
   - Payment tokens, API keys, and auth secrets exposed in source code
   - **Fix**: Moved to environment variables

2. **SQL Injection** (Lines 27-29)
   - String formatting in SQL queries allows malicious SQL execution
   - **Fix**: Implemented parameterized queries

3. **Command Injection** (Lines 49-50)
   - User input passed to shell commands enables arbitrary command execution
   - **Fix**: Input validation + removed shell=True

### High Severity (3)
4. **Server-Side Request Forgery (SSRF)** (Lines 38-39)
   - Unvalidated URL requests can access internal resources
   - **Fix**: Domain whitelist validation

5. **Weak Cryptographic Hash (MD5)** (Line 24)
   - MD5 is cryptographically broken and vulnerable to collisions
   - **Fix**: Replaced with SHA-256

6. **Path Traversal** (Line 45)
   - Unrestricted file access allows reading arbitrary files
   - **Fix**: Path validation with base directory restriction

### Medium Severity (1)
7. **Debug Mode in Production** (Line 85)
   - Flask debug mode exposes sensitive error information
   - **Fix**: Documented best practices (use debug=False or WSGI server)

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Platform-Specific Setup

#### Linux/macOS

1. **Make setup script executable:**
   ```bash
   chmod +x setup.sh
   chmod +x run_test.sh
   ```

2. **Run setup:**
   ```bash
   ./setup.sh
   ```

3. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

4. **Set environment variables:**
   ```bash
   export PAYMENT_TOKEN="your_payment_token"
   export MAIL_SERVER_KEY="your_mail_key"
   export INTERNAL_AUTH="your_internal_auth"
   export ALLOWED_DOMAINS="api.payment-service.com,trusted-domain.com"
   ```

#### Windows

1. **Create virtual environment:**
   ```powershell
   python -m venv venv
   ```

2. **Activate virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Create necessary directories:**
   ```powershell
   mkdir config, logs
   ```

5. **Set environment variables:**
   ```powershell
   $env:PAYMENT_TOKEN="your_payment_token"
   $env:MAIL_SERVER_KEY="your_mail_key"
   $env:INTERNAL_AUTH="your_internal_auth"
   $env:ALLOWED_DOMAINS="api.payment-service.com,trusted-domain.com"
   ```

#### Docker

1. **Build Docker image:**
   ```bash
   docker build -t security-audit-app .
   ```

2. **Run container:**
   ```bash
   docker run -p 5000:5000 \
     -e PAYMENT_TOKEN="your_payment_token" \
     -e MAIL_SERVER_KEY="your_mail_key" \
     -e INTERNAL_AUTH="your_internal_auth" \
     -e ALLOWED_DOMAINS="api.payment-service.com" \
     security-audit-app
   ```

## Running Tests

### Manual Testing

#### Linux/macOS
```bash
./run_test.sh
```

#### Windows
```batch
run_test.bat
```

### Automatic Testing with Environment Detection

The `auto_test.py` script automatically detects your environment and runs the appropriate tests:

```bash
# Linux/macOS/Docker
python3 auto_test.py

# Windows
python auto_test.py
```

**Features of auto_test.py:**
- Detects environment automatically (Windows/Linux/macOS/Docker)
- Tests both `inputs_backup.py` and `inputs.py` in sequence
- Logs all output to `logs/test_run.log` with timestamps
- Provides clear final status: `TEST PASSED` or `TEST FAILED`
- Exit code 0 for success, 1 for failure

### Test Coverage

The test scripts validate:
- ✓ File existence (inputs.py, inputs_backup.py)
- ✓ Removal of hardcoded secrets
- ✓ SQL injection protection (parameterized queries)
- ✓ Command injection protection (shell=False)
- ✓ SSRF protection (domain whitelist)
- ✓ Path traversal protection
- ✓ Secure hashing (SHA-256 vs MD5)
- ✓ Python syntax validation
- ✓ Required security imports

## Checking Test Results

### Log File Location
All test results are saved to: `logs/test_run.log`

### Log File Contents
The log includes:
- **Start timestamp**: When tests began
- **Environment information**: OS, platform, Python version
- **Individual test results**: For each test file
  - Test name (inputs_backup.py, inputs.py)
  - Timestamp
  - Return code
  - Full test output
  - Status (TEST PASSED or TEST FAILED)
- **Final summary**: Overall test status

### Interpreting Results

**TEST PASSED**: All security checks passed
- No hardcoded secrets detected
- All security mitigations verified
- Code syntax is valid

**TEST FAILED**: One or more security checks failed
- Review the log for specific failures
- Check which tests failed and why
- Verify environment variables are set correctly

### Example Log Review

```bash
# Linux/macOS
cat logs/test_run.log | grep "Status:"

# Windows
findstr "Status:" logs\test_run.log
```

## Running the Application

### Development Mode

**⚠️ Warning**: Do not use debug mode in production!

```bash
# Set required environment variables first
python inputs.py
```

### Production Mode

Use a production WSGI server like Gunicorn:

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 inputs:app
```

## API Endpoints

The application exposes the following endpoints:

- **POST `/auth`**: User authentication
- **GET `/profile`**: Retrieve user profile (requires `id` parameter)
- **POST `/transfer`**: Transfer funds
- **POST `/config`**: Update configuration
- **GET `/export`**: Export data (requires `name` parameter)

## Environment Variables

Required environment variables for secure operation:

| Variable | Description | Example |
|----------|-------------|---------|
| `PAYMENT_TOKEN` | Payment service authentication token | `tok_prod_xxx` |
| `MAIL_SERVER_KEY` | Mail server API key | `mail_key_xxx` |
| `INTERNAL_AUTH` | Internal authentication secret | `auth_secret_xxx` |
| `ALLOWED_DOMAINS` | Comma-separated list of allowed domains for SSRF protection | `api.payment.com,api.notify.com` |

## Security Best Practices

### For Production Deployment

1. **Never commit secrets to version control**
   - Use environment variables or secret management systems
   - Add `.env` to `.gitignore`

2. **Disable debug mode**
   - Set `debug=False` in Flask app
   - Use production WSGI servers (Gunicorn, uWSGI)

3. **Use HTTPS**
   - Always use TLS/SSL in production
   - Configure proper SSL certificates

4. **Regular updates**
   - Keep dependencies updated
   - Monitor security advisories

5. **Input validation**
   - Always validate and sanitize user input
   - Use allowlists over denylists

6. **Database security**
   - Always use parameterized queries
   - Implement proper access controls

7. **Least privilege principle**
   - Run applications with minimal required permissions
   - Use separate accounts for different services

## Troubleshooting

### Common Issues

**Issue**: Tests fail with "command not found"
- **Solution**: Ensure scripts have execute permissions (`chmod +x script.sh`)

**Issue**: Python module not found
- **Solution**: Activate virtual environment and run `pip install -r requirements.txt`

**Issue**: Environment variables not set
- **Solution**: Export/set all required environment variables before running

**Issue**: Database file errors
- **Solution**: Ensure write permissions in the application directory

**Issue**: Docker container won't start
- **Solution**: Check environment variables are passed correctly with `-e` flags

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/stable/security/)
- [Python Security Guide](https://python.readthedocs.io/en/stable/library/security_warnings.html)

## License

This is a security audit demonstration project. Use at your own risk.

## Contact

For questions or issues, please review the `report.json` file for detailed vulnerability information.

---

**Last Updated**: December 4, 2025
