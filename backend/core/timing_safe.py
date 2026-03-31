"""
Timing-safe comparison utilities to prevent timing attacks.

Timing attacks can leak information about correct/incorrect values
by measuring how long comparisons take. This module provides
constant-time comparison functions.
"""

import hmac
from typing import Union


def constant_time_compare(a: Union[str, bytes], b: Union[str, bytes]) -> bool:
    """
    Compare two strings/bytes in constant time.
    
    Prevents timing attacks by always taking the same amount of time
    regardless of where the values differ.
    
    Args:
        a: First value to compare
        b: Second value to compare
        
    Returns:
        True if values are equal, False otherwise
        
    Example:
        # Safe for comparing user-provided room codes
        if constant_time_compare(code, expected_code):
            # ... process match
    """
    if isinstance(a, str):
        a = a.encode('utf-8')
    if isinstance(b, str):
        b = b.encode('utf-8')
    
    return hmac.compare_digest(a, b)
