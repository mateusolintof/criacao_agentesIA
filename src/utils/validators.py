"""
Validadores de input para agentes de IA.
"""

import re
from typing import Tuple


def validate_email(email: str) -> bool:
    """
    Valida formato de email.

    Args:
        email: String de email a validar

    Returns:
        True se válido, False caso contrário
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Valida telefone brasileiro.

    Args:
        phone: Telefone a validar (aceita formatação)

    Returns:
        True se válido (10-11 dígitos), False caso contrário
    """
    digits = ''.join(filter(str.isdigit, phone))
    return len(digits) >= 10 and len(digits) <= 11


def sanitize_input(text: str, max_length: int = 2000) -> str:
    """
    Sanitiza input do usuário.

    Args:
        text: Texto a sanitizar
        max_length: Tamanho máximo permitido

    Returns:
        Texto sanitizado
    """
    # Remover espaços extras
    text = ' '.join(text.split())

    # Limitar tamanho
    text = text[:max_length]

    # Remover caracteres potencialmente perigosos
    dangerous_patterns = [
        r'<script.*?>.*?</script>',  # XSS
        r'javascript:',              # XSS
        r'on\w+\s*=',               # Event handlers
    ]

    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    return text.strip()


def check_prompt_injection(text: str) -> Tuple[bool, str]:
    """
    Detecta tentativas de prompt injection.

    Args:
        text: Texto a verificar

    Returns:
        Tuple (is_injection, reason)
    """
    injection_patterns = [
        (r'ignore\s+(all\s+)?previous\s+instructions?', 'ignore_instructions'),
        (r'disregard\s+(all\s+)?previous', 'disregard'),
        (r'forget\s+everything', 'forget'),
        (r'you\s+are\s+now', 'role_change'),
        (r'new\s+instructions?:', 'new_instructions'),
    ]

    text_lower = text.lower()

    for pattern, reason in injection_patterns:
        if re.search(pattern, text_lower):
            return True, reason

    return False, ""
