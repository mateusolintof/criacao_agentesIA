"""
Utilidades compartilhadas do framework.
"""

from .validators import validate_email, validate_phone, sanitize_input
from .formatters import format_currency, format_phone
from .retry import retry_with_backoff
from .cache import SimpleCache

__all__ = [
    'validate_email',
    'validate_phone',
    'sanitize_input',
    'format_currency',
    'format_phone',
    'retry_with_backoff',
    'SimpleCache',
]
