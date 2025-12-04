# Security Vulnerabilities Summary

## File: inputs.py (Original Vulnerable Version - now backed up as inputs_backup.py)

### Critical Vulnerabilities

1. **Hardcoded Secrets**
   - File: inputs.py
   - Lines: 11, 12, 13
   - Type: Hardcoded Sensitive Credentials
   - Severity: Critical
   - Details: PAYMENT_TOKEN, MAIL_SERVER_KEY, and INTERNAL_AUTH are hardcoded

2. **SQL Injection**
   - File: inputs.py
   - Lines: 27, 28, 29
   - Type: SQL Injection via String Formatting
   - Severity: Critical
   - Details: query_profile() function uses string formatting for SQL queries

3. **Command Injection**
   - File: inputs.py
   - Lines: 49, 50
   - Type: OS Command Injection
   - Severity: Critical
   - Details: export_data() function uses shell=True with user input

### High Severity Vulnerabilities

4. **Server-Side Request Forgery (SSRF)**
   - File: inputs.py
   - Lines: 38, 39
   - Type: SSRF - Unvalidated URL Requests
   - Severity: High
   - Details: transfer_funds() makes requests to user-controlled URLs

5. **Weak Cryptographic Hash**
   - File: inputs.py
   - Line: 24
   - Type: Use of Broken Cryptographic Algorithm (MD5)
   - Severity: High
   - Details: auth_user() uses MD5 for hashing

6. **Path Traversal**
   - File: inputs.py
   - Line: 45
   - Type: Directory Traversal / Path Traversal
   - Severity: High
   - Details: update_records() opens files without path validation

### Medium Severity Vulnerabilities

7. **Debug Mode Enabled**
   - File: inputs.py
   - Line: 85
   - Type: Information Disclosure
   - Severity: Medium
   - Details: Flask application runs with debug=True

---

## All Vulnerabilities Fixed in: inputs.py (Secured Version)

All 7 vulnerabilities have been remediated with secure coding practices.
See report.json for detailed fix explanations and secure code snippets.
