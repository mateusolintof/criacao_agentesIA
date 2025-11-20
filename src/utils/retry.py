"""
Utilitários de retry com backoff exponencial.
"""

import time
import logging
from typing import Callable, Any, List, Type
from functools import wraps


logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: List[Type[Exception]] = None
):
    """
    Decorator para retry com backoff exponencial.

    Args:
        max_retries: Número máximo de tentativas
        initial_delay: Delay inicial em segundos
        backoff_factor: Fator de multiplicação do delay
        exceptions: Lista de exceções que devem causar retry

    Returns:
        Decorator function
    """
    if exceptions is None:
        exceptions = [Exception]

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except tuple(exceptions) as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            f"Failed after {max_retries} retries: {func.__name__}",
                            exc_info=True
                        )
                        raise

                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay}s..."
                    )

                    time.sleep(delay)
                    delay *= backoff_factor

            # Should never reach here, but just in case
            raise last_exception

        return wrapper
    return decorator


class CircuitBreaker:
    """
    Implementação simples de Circuit Breaker pattern.

    Estados:
    - CLOSED: Normal, permite chamadas
    - OPEN: Muitas falhas, bloqueia chamadas
    - HALF_OPEN: Testando recuperação
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: float = 60.0
    ):
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função através do circuit breaker."""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.timeout:
                logger.info("Circuit breaker transitioning to HALF_OPEN")
                self.state = "HALF_OPEN"
                self.success_count = 0
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)

            # Sucesso
            if self.state == "HALF_OPEN":
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    logger.info("Circuit breaker transitioning to CLOSED")
                    self.state = "CLOSED"
                    self.failure_count = 0

            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                logger.warning("Circuit breaker transitioning to OPEN")
                self.state = "OPEN"

            raise e
