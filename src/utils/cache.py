"""
Utilitários de cache simples.
"""

import time
from typing import Any, Optional, Dict
from dataclasses import dataclass


@dataclass
class CacheEntry:
    """Entrada de cache com TTL."""
    value: Any
    expires_at: float


class SimpleCache:
    """Cache simples em memória com TTL."""

    def __init__(self, default_ttl: int = 300):
        """
        Inicializa cache.

        Args:
            default_ttl: Tempo de vida padrão em segundos
        """
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}

    def get(self, key: str) -> Optional[Any]:
        """
        Recupera valor do cache.

        Args:
            key: Chave do cache

        Returns:
            Valor se existe e não expirou, None caso contrário
        """
        if key not in self._cache:
            return None

        entry = self._cache[key]

        # Verificar expiração
        if time.time() > entry.expires_at:
            del self._cache[key]
            return None

        return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Armazena valor no cache.

        Args:
            key: Chave do cache
            value: Valor a armazenar
            ttl: Tempo de vida em segundos (usa default se None)
        """
        if ttl is None:
            ttl = self.default_ttl

        expires_at = time.time() + ttl

        self._cache[key] = CacheEntry(
            value=value,
            expires_at=expires_at
        )

    def delete(self, key: str):
        """Remove entrada do cache."""
        if key in self._cache:
            del self._cache[key]

    def clear(self):
        """Limpa todo o cache."""
        self._cache.clear()

    def cleanup_expired(self):
        """Remove entradas expiradas."""
        now = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if now > entry.expires_at
        ]

        for key in expired_keys:
            del self._cache[key]

    def __len__(self) -> int:
        """Retorna número de entradas no cache."""
        return len(self._cache)
