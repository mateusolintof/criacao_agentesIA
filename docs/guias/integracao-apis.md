# Guia: Integração com APIs Externas

## Visão Geral

Este guia ensina como integrar agentes de IA com APIs externas (CRM, ERP, pagamentos, etc) de forma robusta, segura e eficiente. Você aprenderá padrões de integração, tratamento de erros, caching e melhores práticas.

## Índice

1. [Planejamento da Integração](#planejamento-da-integração)
2. [Implementar Client Base](#implementar-client-base)
3. [Autenticação](#autenticação)
4. [Retry Logic](#retry-logic)
5. [Rate Limiting](#rate-limiting)
6. [Caching](#caching)
7. [Tratamento de Erros](#tratamento-de-erros)
8. [Testes](#testes)
9. [Monitoramento](#monitoramento)
10. [Exemplos Práticos](#exemplos-práticos)

## Planejamento da Integração

### Passo 1: Documentar API

```bash
# Copiar template de especificação
cp templates/integracao/template-spec-api.md docs/integracoes/crm-api.md
```

Preencher informações essenciais:

```markdown
# Integração: CRM API

## Informações Gerais
- **API**: Salesforce CRM
- **Versão**: v55.0
- **Base URL**: https://yourinstance.salesforce.com/services/data/v55.0
- **Documentação**: https://developer.salesforce.com/docs
- **Autenticação**: OAuth 2.0

## Endpoints Utilizados

### 1. Criar Lead
- **Método**: POST
- **Path**: `/sobjects/Lead`
- **Rate Limit**: 100 req/min
- **Timeout**: 10s

### 2. Buscar Contato
- **Método**: GET
- **Path**: `/sobjects/Contact/{id}`
- **Rate Limit**: 500 req/min
- **Timeout**: 5s

## Dependências
- Requer token OAuth válido
- Cliente deve ter permissão de criar leads

## SLA
- Disponibilidade: 99.9%
- Response time p95: < 500ms

## Contatos
- Equipe: team@salesforce.com
- Suporte: suporte@cliente.com
```

### Passo 2: Mapear Dados

```python
# Mapeamento de dados internos -> API
LEAD_MAPPING = {
    # Campo interno: Campo da API
    "company_name": "Company",
    "contact_name": "FirstName + LastName",
    "email": "Email",
    "phone": "Phone",
    "company_size": "NumberOfEmployees",
    "budget": "Budget__c",  # Campo custom
    "source": "LeadSource"
}

# Validações necessárias
LEAD_VALIDATIONS = {
    "Company": {"required": True, "max_length": 255},
    "Email": {"required": True, "format": "email"},
    "Phone": {"required": False, "format": "phone"}
}
```

## Implementar Client Base

### Client Genérico Reutilizável

```python
# src/integrations/base_api_client.py
"""
Client base para integrações com APIs externas.

Fornece funcionalidade comum: retry, timeout, logging, métricas.
"""

import requests
import logging
import time
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from functools import wraps
import hashlib
import json


class APIError(Exception):
    """Erro genérico de API"""
    pass


class AuthenticationError(APIError):
    """Erro de autenticação"""
    pass


class RateLimitError(APIError):
    """Rate limit excedido"""
    pass


class BaseAPIClient:
    """
    Client base para APIs externas.

    Funcionalidades:
    - Retry automático com exponential backoff
    - Timeout configurável
    - Logging estruturado
    - Métricas de latência e erro
    - Cache opcional
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 10,
        max_retries: int = 3,
        retry_backoff: float = 0.3,
        logger: Optional[logging.Logger] = None
    ):
        """
        Inicializa client.

        Args:
            base_url: URL base da API
            api_key: Chave de autenticação
            timeout: Timeout em segundos
            max_retries: Número máximo de retries
            retry_backoff: Fator de backoff exponencial
            logger: Logger customizado
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logger or logging.getLogger(__name__)

        # Configurar sessão com retry
        self.session = self._create_session(max_retries, retry_backoff)

        # Métricas
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_latency": 0.0,
            "errors_by_type": {}
        }

        self.logger.info(f"API Client initialized: {base_url}")

    def _create_session(self, max_retries: int, backoff: float) -> requests.Session:
        """
        Cria sessão com retry automático.

        Args:
            max_retries: Número de retries
            backoff: Fator de backoff

        Returns:
            Session configurada
        """
        session = requests.Session()

        # Configurar retry strategy
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],  # Status codes para retry
            method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
            backoff_factor=backoff  # 0.3 -> 0.3s, 0.6s, 1.2s
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _get_headers(self) -> Dict[str, str]:
        """
        Retorna headers padrão.

        Override em subclasses para autenticação específica.
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "AI-Agent-Integration/1.0"
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Faz request HTTP.

        Args:
            method: HTTP method (GET, POST, etc)
            endpoint: Endpoint path
            data: Request body
            params: Query parameters
            headers: Headers adicionais

        Returns:
            Response data

        Raises:
            APIError: Erro na API
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Merge headers
        request_headers = self._get_headers()
        if headers:
            request_headers.update(headers)

        # Log request
        self.logger.debug(f"API Request: {method} {url}")
        if data:
            self.logger.debug(f"Request data: {json.dumps(data, indent=2)}")

        start_time = time.time()

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=request_headers,
                timeout=self.timeout
            )

            latency = time.time() - start_time

            # Atualizar métricas
            self._update_metrics(success=response.ok, latency=latency)

            # Log response
            self.logger.debug(
                f"API Response: {response.status_code} "
                f"(latency: {latency:.2f}s)"
            )

            # Verificar erros
            if response.status_code == 401:
                raise AuthenticationError("Authentication failed")

            elif response.status_code == 429:
                retry_after = response.headers.get('Retry-After', 60)
                raise RateLimitError(f"Rate limit exceeded. Retry after {retry_after}s")

            elif response.status_code >= 400:
                error_msg = self._parse_error(response)
                raise APIError(f"API Error {response.status_code}: {error_msg}")

            # Parse response
            try:
                return response.json()
            except ValueError:
                # Resposta não é JSON
                return {"response": response.text, "status_code": response.status_code}

        except requests.exceptions.Timeout:
            self.logger.error(f"Request timeout: {url}")
            self._update_metrics(success=False, latency=self.timeout)
            raise APIError(f"Request timeout after {self.timeout}s")

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {url} - {e}")
            self._update_metrics(success=False, latency=time.time() - start_time)
            raise APIError(f"Connection error: {str(e)}")

        except (AuthenticationError, RateLimitError):
            # Re-raise estas exceções
            raise

        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            self._update_metrics(success=False, latency=time.time() - start_time)
            raise APIError(f"Unexpected error: {str(e)}")

    def _parse_error(self, response: requests.Response) -> str:
        """
        Parse mensagem de erro da resposta.

        Args:
            response: Response object

        Returns:
            Mensagem de erro
        """
        try:
            error_data = response.json()
            # Tentar extrair mensagem (varia por API)
            return (
                error_data.get('message') or
                error_data.get('error') or
                error_data.get('error_description') or
                str(error_data)
            )
        except ValueError:
            return response.text

    def _update_metrics(self, success: bool, latency: float):
        """Atualiza métricas do client."""
        self.metrics["total_requests"] += 1

        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1

        self.metrics["total_latency"] += latency

    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Dict:
        """GET request."""
        return self._make_request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict:
        """POST request."""
        return self._make_request("POST", endpoint, data=data, **kwargs)

    def put(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict:
        """PUT request."""
        return self._make_request("PUT", endpoint, data=data, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Dict:
        """DELETE request."""
        return self._make_request("DELETE", endpoint, **kwargs)

    def get_metrics(self) -> Dict[str, Any]:
        """
        Retorna métricas do client.

        Returns:
            Dict com métricas
        """
        total = self.metrics["total_requests"]
        avg_latency = (
            self.metrics["total_latency"] / total
            if total > 0
            else 0
        )

        return {
            "total_requests": total,
            "successful_requests": self.metrics["successful_requests"],
            "failed_requests": self.metrics["failed_requests"],
            "success_rate": (
                self.metrics["successful_requests"] / total
                if total > 0
                else 0
            ),
            "average_latency": avg_latency
        }

    def health_check(self) -> bool:
        """
        Verifica saúde da API.

        Returns:
            True se API está respondendo
        """
        try:
            # Implementar endpoint de health check específico
            self.get("/health")
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
```

### Client Específico (CRM)

```python
# src/integrations/crm_client.py
"""
Client para integração com CRM.
"""

from integrations.base_api_client import BaseAPIClient, APIError
from typing import Dict, Any, List, Optional
import os


class CRMClient(BaseAPIClient):
    """
    Client para CRM API.

    Funcionalidades:
    - Criar/atualizar leads
    - Buscar contatos
    - Criar oportunidades
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ):
        """
        Inicializa CRM client.

        Args:
            api_key: API key (ou usa env var CRM_API_KEY)
            base_url: Base URL (ou usa env var CRM_API_URL)
        """
        api_key = api_key or os.getenv("CRM_API_KEY")
        base_url = base_url or os.getenv("CRM_API_URL")

        if not api_key or not base_url:
            raise ValueError("CRM_API_KEY and CRM_API_URL are required")

        super().__init__(base_url, api_key, **kwargs)

    def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria lead no CRM.

        Args:
            lead_data: Dados do lead

        Returns:
            Dict com lead_id e status

        Example:
            >>> client = CRMClient()
            >>> result = client.create_lead({
            ...     "company_name": "Acme Corp",
            ...     "contact_name": "John Doe",
            ...     "email": "john@acme.com",
            ...     "phone": "11999999999",
            ...     "source": "chatbot"
            ... })
            >>> print(result["lead_id"])
        """
        # Validar dados
        self._validate_lead_data(lead_data)

        # Mapear para formato da API
        api_payload = self._map_lead_data(lead_data)

        # Fazer request
        try:
            response = self.post("/leads", data=api_payload)

            self.logger.info(f"Lead created: {response.get('id')}")

            return {
                "success": True,
                "lead_id": response.get("id"),
                "message": "Lead created successfully"
            }

        except APIError as e:
            self.logger.error(f"Failed to create lead: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_lead(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca lead por ID.

        Args:
            lead_id: ID do lead

        Returns:
            Dados do lead ou None
        """
        try:
            response = self.get(f"/leads/{lead_id}")
            return response

        except APIError as e:
            self.logger.error(f"Failed to get lead {lead_id}: {e}")
            return None

    def update_lead(
        self,
        lead_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Atualiza lead existente.

        Args:
            lead_id: ID do lead
            updates: Campos a atualizar

        Returns:
            Resultado da operação
        """
        try:
            response = self.put(f"/leads/{lead_id}", data=updates)

            return {
                "success": True,
                "message": "Lead updated successfully"
            }

        except APIError as e:
            self.logger.error(f"Failed to update lead {lead_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def search_leads(
        self,
        filters: Dict[str, Any],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Busca leads com filtros.

        Args:
            filters: Filtros de busca
            limit: Limite de resultados

        Returns:
            Lista de leads
        """
        try:
            params = {**filters, "limit": limit}
            response = self.get("/leads", params=params)

            return response.get("leads", [])

        except APIError as e:
            self.logger.error(f"Failed to search leads: {e}")
            return []

    def create_opportunity(
        self,
        lead_id: str,
        opportunity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Converte lead em oportunidade.

        Args:
            lead_id: ID do lead
            opportunity_data: Dados da oportunidade

        Returns:
            Resultado da operação
        """
        try:
            payload = {
                "lead_id": lead_id,
                **opportunity_data
            }

            response = self.post("/opportunities", data=payload)

            return {
                "success": True,
                "opportunity_id": response.get("id")
            }

        except APIError as e:
            self.logger.error(f"Failed to create opportunity: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # ========== MÉTODOS PRIVADOS ==========

    def _validate_lead_data(self, data: Dict[str, Any]):
        """
        Valida dados do lead.

        Raises:
            ValueError: Se dados inválidos
        """
        required_fields = ["company_name", "contact_name", "email"]

        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Required field missing: {field}")

        # Validar email
        if "@" not in data["email"]:
            raise ValueError(f"Invalid email: {data['email']}")

    def _map_lead_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapeia dados internos para formato da API.

        Args:
            data: Dados internos

        Returns:
            Dados no formato da API
        """
        # Mapear campos
        return {
            "Company": data.get("company_name"),
            "FirstName": data.get("contact_name", "").split()[0],
            "LastName": " ".join(data.get("contact_name", "").split()[1:]) or ".",
            "Email": data.get("email"),
            "Phone": data.get("phone"),
            "NumberOfEmployees": data.get("company_size"),
            "Budget__c": data.get("budget"),
            "LeadSource": data.get("source", "chatbot"),
            "Description": data.get("notes"),
            "Status": "New"
        }
```

## Autenticação

### OAuth 2.0

```python
# src/integrations/oauth_client.py
"""
Client com OAuth 2.0.
"""

from integrations.base_api_client import BaseAPIClient
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional


class OAuthClient(BaseAPIClient):
    """Client com autenticação OAuth 2.0"""

    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        token_url: str,
        **kwargs
    ):
        """
        Inicializa OAuth client.

        Args:
            base_url: URL base da API
            client_id: Client ID
            client_secret: Client secret
            token_url: URL para obter token
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url

        # Token storage
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None

        # Obter token inicial
        self._refresh_token()

        super().__init__(base_url, api_key="", **kwargs)

    def _refresh_token(self):
        """Obtém novo access token."""
        try:
            response = requests.post(
                self.token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                },
                timeout=10
            )

            response.raise_for_status()
            token_data = response.json()

            self.access_token = token_data["access_token"]

            # Calcular expiração (geralmente expires_in em segundos)
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

            self.logger.info("OAuth token refreshed successfully")

        except Exception as e:
            self.logger.error(f"Failed to refresh token: {e}")
            raise

    def _is_token_expired(self) -> bool:
        """Verifica se token expirou."""
        if not self.token_expires_at:
            return True

        # Renovar 5 minutos antes de expirar
        return datetime.utcnow() >= (self.token_expires_at - timedelta(minutes=5))

    def _get_headers(self) -> Dict[str, str]:
        """Retorna headers com token atualizado."""
        # Verificar se precisa renovar
        if self._is_token_expired():
            self._refresh_token()

        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
```

### API Key

```python
def _get_headers(self) -> Dict[str, str]:
    """Headers com API key."""
    return {
        "X-API-Key": self.api_key,
        "Content-Type": "application/json"
    }
```

### Basic Auth

```python
from requests.auth import HTTPBasicAuth

def _make_request(self, method, endpoint, **kwargs):
    """Request com basic auth."""
    auth = HTTPBasicAuth(self.username, self.password)
    return super()._make_request(method, endpoint, auth=auth, **kwargs)
```

## Retry Logic

Já implementado no `BaseAPIClient`, mas você pode customizar:

```python
def custom_retry_logic(self, func, max_attempts=3):
    """
    Retry customizado com backoff exponencial.

    Args:
        func: Função a executar
        max_attempts: Tentativas máximas

    Returns:
        Resultado da função
    """
    attempt = 0
    last_exception = None

    while attempt < max_attempts:
        try:
            return func()

        except RateLimitError as e:
            # Para rate limit, esperar tempo indicado
            retry_after = self._extract_retry_after(e)
            self.logger.warning(f"Rate limited. Waiting {retry_after}s")
            time.sleep(retry_after)
            attempt += 1
            last_exception = e

        except APIError as e:
            # Para outros erros, backoff exponencial
            wait_time = (2 ** attempt) * 0.5  # 0.5s, 1s, 2s, 4s...
            self.logger.warning(f"API error. Retrying in {wait_time}s")
            time.sleep(wait_time)
            attempt += 1
            last_exception = e

    # Todas tentativas falharam
    raise last_exception
```

## Rate Limiting

### Client-Side Rate Limiting

```python
# src/integrations/rate_limiter.py
"""
Rate limiter para controlar requests.
"""

import time
from collections import deque
from threading import Lock


class RateLimiter:
    """
    Rate limiter usando sliding window.

    Limita número de requests por período.
    """

    def __init__(self, max_requests: int, time_window: int):
        """
        Inicializa rate limiter.

        Args:
            max_requests: Máximo de requests
            time_window: Janela de tempo em segundos
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        self.lock = Lock()

    def acquire(self):
        """
        Adquire permissão para fazer request.

        Bloqueia se rate limit excedido.
        """
        with self.lock:
            now = time.time()

            # Remover requests antigos
            while self.requests and self.requests[0] < now - self.time_window:
                self.requests.popleft()

            # Verificar se pode fazer request
            if len(self.requests) >= self.max_requests:
                # Calcular quanto tempo esperar
                oldest_request = self.requests[0]
                wait_time = self.time_window - (now - oldest_request)

                if wait_time > 0:
                    time.sleep(wait_time)
                    return self.acquire()  # Tentar novamente

            # Registrar request
            self.requests.append(now)


# Uso no client
class RateLimitedClient(BaseAPIClient):
    """Client com rate limiting."""

    def __init__(self, *args, requests_per_minute=60, **kwargs):
        super().__init__(*args, **kwargs)

        # 60 requests por minuto
        self.rate_limiter = RateLimiter(
            max_requests=requests_per_minute,
            time_window=60
        )

    def _make_request(self, *args, **kwargs):
        """Request com rate limiting."""
        self.rate_limiter.acquire()
        return super()._make_request(*args, **kwargs)
```

## Caching

```python
# src/integrations/cached_client.py
"""
Client com caching para reduzir requests.
"""

from integrations.base_api_client import BaseAPIClient
import hashlib
import json
import time
from typing import Dict, Any, Optional


class CachedClient(BaseAPIClient):
    """Client com cache em memória."""

    def __init__(self, *args, cache_ttl: int = 300, **kwargs):
        """
        Inicializa cached client.

        Args:
            cache_ttl: Time-to-live do cache em segundos (default: 5min)
        """
        super().__init__(*args, **kwargs)
        self.cache_ttl = cache_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}

    def _get_cache_key(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None
    ) -> str:
        """
        Gera chave de cache.

        Args:
            method: HTTP method
            endpoint: Endpoint
            params: Parameters

        Returns:
            Cache key
        """
        cache_input = f"{method}:{endpoint}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(cache_input.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Busca no cache.

        Returns:
            Cached data ou None
        """
        if cache_key in self.cache:
            cached = self.cache[cache_key]

            # Verificar se ainda é válido
            if time.time() < cached["expires_at"]:
                self.logger.debug(f"Cache hit: {cache_key}")
                return cached["data"]

            # Expirado, remover
            del self.cache[cache_key]

        return None

    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]):
        """Salva no cache."""
        self.cache[cache_key] = {
            "data": data,
            "expires_at": time.time() + self.cache_ttl
        }

        self.logger.debug(f"Cached: {cache_key}")

    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Dict:
        """GET com cache."""
        # Verificar cache
        cache_key = self._get_cache_key("GET", endpoint, params)
        cached_data = self._get_from_cache(cache_key)

        if cached_data is not None:
            return cached_data

        # Cache miss, fazer request
        data = super().get(endpoint, params=params, **kwargs)

        # Salvar no cache
        self._save_to_cache(cache_key, data)

        return data

    def clear_cache(self):
        """Limpa cache."""
        self.cache.clear()
        self.logger.info("Cache cleared")
```

## Tratamento de Erros

```python
def robust_api_call(self, func, *args, **kwargs):
    """
    Wrapper para chamadas de API com tratamento robusto.

    Args:
        func: Função da API a chamar
        *args, **kwargs: Argumentos

    Returns:
        Resultado ou fallback
    """
    try:
        return func(*args, **kwargs)

    except AuthenticationError:
        # Autenticação falhou - critical
        self.logger.critical("Authentication failed!")
        # Notificar equipe
        self._alert_team("API auth failed")
        raise

    except RateLimitError as e:
        # Rate limit - esperar e tentar novamente
        self.logger.warning(f"Rate limited: {e}")
        return {"success": False, "error": "rate_limit", "retry": True}

    except APIError as e:
        # Erro de API - retornar erro estruturado
        self.logger.error(f"API error: {e}")
        return {
            "success": False,
            "error": "api_error",
            "message": str(e),
            "fallback": self._get_fallback_data()
        }

    except Exception as e:
        # Erro inesperado
        self.logger.exception(f"Unexpected error: {e}")
        return {
            "success": False,
            "error": "unexpected",
            "message": "Erro inesperado ao acessar sistema externo"
        }


def _get_fallback_data(self):
    """Retorna dados de fallback quando API falha."""
    return {
        "message": "Dados temporariamente indisponíveis",
        "suggestion": "Por favor, tente novamente em alguns minutos"
    }
```

## Testes

```python
# tests/unit/test_crm_client.py
import pytest
from unittest.mock import Mock, patch
from integrations.crm_client import CRMClient, APIError
import requests


@pytest.fixture
def crm_client():
    """Fixture do CRM client"""
    return CRMClient(
        api_key="test_key",
        base_url="https://test.api.com"
    )


def test_create_lead_success(crm_client):
    """Testa criação de lead bem-sucedida"""
    with patch.object(crm_client, 'post') as mock_post:
        mock_post.return_value = {"id": "lead_123"}

        result = crm_client.create_lead({
            "company_name": "Test Corp",
            "contact_name": "John Doe",
            "email": "john@test.com"
        })

        assert result["success"] is True
        assert result["lead_id"] == "lead_123"
        mock_post.assert_called_once()


def test_create_lead_validation_error(crm_client):
    """Testa validação de dados"""
    with pytest.raises(ValueError):
        crm_client.create_lead({
            "company_name": "Test Corp"
            # Faltando campos obrigatórios
        })


def test_create_lead_api_error(crm_client):
    """Testa erro da API"""
    with patch.object(crm_client, 'post') as mock_post:
        mock_post.side_effect = APIError("API Error")

        result = crm_client.create_lead({
            "company_name": "Test Corp",
            "contact_name": "John Doe",
            "email": "john@test.com"
        })

        assert result["success"] is False
        assert "error" in result


def test_rate_limiting(crm_client):
    """Testa rate limiting"""
    # Configurar rate limiter
    crm_client.rate_limiter = RateLimiter(max_requests=2, time_window=1)

    # Fazer 3 requests
    start = time.time()

    crm_client.get("/test")
    crm_client.get("/test")
    crm_client.get("/test")  # Esta deve esperar

    elapsed = time.time() - start

    # Deve ter esperado ~1 segundo
    assert elapsed >= 1.0


def test_caching(cached_client):
    """Testa cache"""
    with patch.object(cached_client.session, 'request') as mock_request:
        mock_request.return_value = Mock(
            ok=True,
            status_code=200,
            json=lambda: {"data": "test"}
        )

        # Primeira chamada
        result1 = cached_client.get("/endpoint")

        # Segunda chamada (deve vir do cache)
        result2 = cached_client.get("/endpoint")

        # Apenas 1 request real
        assert mock_request.call_count == 1
        assert result1 == result2
```

## Monitoramento

```python
# Métricas importantes
def log_api_metrics(client: BaseAPIClient):
    """Log métricas da API"""
    metrics = client.get_metrics()

    logger.info(f"""
    API Metrics:
    - Total Requests: {metrics['total_requests']}
    - Success Rate: {metrics['success_rate']:.2%}
    - Avg Latency: {metrics['average_latency']:.2f}s
    - Failed Requests: {metrics['failed_requests']}
    """)

    # Enviar para sistema de monitoramento
    send_to_monitoring_system({
        "service": "crm_integration",
        **metrics
    })
```

## Exemplos Práticos

### Integração com Stripe (Pagamentos)

```python
class StripeClient(BaseAPIClient):
    """Client para Stripe API"""

    def create_payment_intent(
        self,
        amount: int,
        currency: str = "brl",
        customer_email: str = None
    ) -> Dict[str, Any]:
        """Cria payment intent"""
        try:
            payload = {
                "amount": amount,
                "currency": currency,
                "payment_method_types": ["card"],
                "receipt_email": customer_email
            }

            response = self.post("/payment_intents", data=payload)

            return {
                "success": True,
                "client_secret": response["client_secret"],
                "payment_intent_id": response["id"]
            }

        except APIError as e:
            return {"success": False, "error": str(e)}
```

### Integração com SendGrid (Email)

```python
class SendGridClient(BaseAPIClient):
    """Client para SendGrid API"""

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: str = "noreply@empresa.com"
    ) -> Dict[str, Any]:
        """Envia email"""
        try:
            payload = {
                "personalizations": [{"to": [{"email": to}]}],
                "from": {"email": from_email},
                "subject": subject,
                "content": [{"type": "text/html", "value": body}]
            }

            response = self.post("/mail/send", data=payload)

            return {"success": True, "message_id": response.get("message_id")}

        except APIError as e:
            return {"success": False, "error": str(e)}
```

## Próximos Passos

- [Testes de Integração](testes-integracao.md)
- [Monitoramento](monitoramento.md)
- [Troubleshooting](troubleshooting.md)

## Referências

- [Template de Especificação de API](../../templates/integracao/template-spec-api.md)
- [Requests Documentation](https://docs.python-requests.org/)
- [Best Practices for API Integration](https://restfulapi.net/)
