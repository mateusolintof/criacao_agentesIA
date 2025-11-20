"""
Formatadores de dados.
"""


def format_currency(value: float, currency: str = "BRL") -> str:
    """
    Formata valor como moeda.

    Args:
        value: Valor numérico
        currency: Código da moeda (BRL, USD, etc)

    Returns:
        String formatada
    """
    if currency == "BRL":
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    elif currency == "USD":
        return f"${value:,.2f}"
    else:
        return f"{value:,.2f} {currency}"


def format_phone(phone: str) -> str:
    """
    Formata telefone brasileiro.

    Args:
        phone: Telefone (apenas números)

    Returns:
        Telefone formatado
    """
    digits = ''.join(filter(str.isdigit, phone))

    if len(digits) == 11:  # Celular com DDD
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    elif len(digits) == 10:  # Fixo com DDD
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    else:
        return phone


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Trunca texto mantendo palavras completas.

    Args:
        text: Texto a truncar
        max_length: Tamanho máximo
        suffix: Sufixo a adicionar

    Returns:
        Texto truncado
    """
    if len(text) <= max_length:
        return text

    truncated = text[:max_length - len(suffix)].rsplit(' ', 1)[0]
    return truncated + suffix
