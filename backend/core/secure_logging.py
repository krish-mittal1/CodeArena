"""
Secure logging utilities to prevent sensitive data leaks.

- Redacts PII (emails, passwords, tokens)
- Prevents credential exposure in logs
- Complies with GDPR/privacy regulations
"""

import re
from typing import Any, Dict


def redact_sensitive_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Redact sensitive fields from data structures before logging.
    
    Removes or masks:
    - Passwords, tokens, keys
    - Email addresses
    - User credentials
    """
    redacted = dict(data)
    
    sensitive_keys = {
        'password', 'password_hash', 'token', 'access_token', 
        'refresh_token', 'jwt', 'secret', 'api_key', 'otp',
        'email', 'phone', 'ssn', 'credit_card'
    }
    
    for key in list(redacted.keys()):
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            redacted[key] = "***REDACTED***"
    
    return redacted


def redact_token(token: str) -> str:
    """Redact JWT token for logging (show only first 20 chars)."""
    if not token or len(token) < 20:
        return "***REDACTED***"
    return f"{token[:20]}...***"


def redact_email(email: str) -> str:
    """Redact email for logging (show only domain)."""
    if not email or '@' not in email:
        return "***REDACTED***"
    local, domain = email.rsplit('@', 1)
    return f"***@{domain}"


def sanitize_log_message(message: str) -> str:
    """
    Remove sensitive patterns from log messages.
    
    Detects and masks:
    - Email addresses
    - URLs with credentials
    - JWT tokens
    """
    # Mask email addresses
    message = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', lambda m: redact_email(m.group()), message)
    
    # Mask URLs with credentials (http://user:pass@host)
    message = re.sub(r'://[^:]+:[^@]+@', '://***:***@', message)
    
    # Mask JWT tokens (bearer token in headers)
    message = re.sub(r'Bearer\s+[A-Za-z0-9\-_\.]+', lambda m: f"Bearer {redact_token(m.group()[7:])}", message)
    
    return message
