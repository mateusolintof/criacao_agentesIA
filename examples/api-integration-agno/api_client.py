"""
API Client com Retry Logic e Error Handling
Atualizado: 2025-11-20
"""

import os
import time
from typing import Optional, Dict, Any, List
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from pydantic import BaseModel


class APIError(Exception):
    """Erro customizado para problemas de API."""
    pass


class Customer(BaseModel):
    """Modelo de cliente."""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    status: str = "active"


class Deal(BaseModel):
    """Modelo de negociação."""
    id: str
    title: str
    value: float
    customer_id: str
    stage: str
    probability: int
    expected_close_date: Optional[str] = None


class CRMAPIClient:
    """Cliente para integração com CRM API."""
    
    def __init__(
        self,
        base_url: str = None,
        api_key: str = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Inicializa o client.
        
        Args:
            base_url: URL base da API
            api_key: Chave de API
            timeout: Timeout em segundos
            max_retries: Número máximo de tentativas
        """
        self.base_url = base_url or os.getenv("CRM_API_URL", "http://localhost:8001")
        self.api_key = api_key or os.getenv("CRM_API_KEY", "")
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Headers padrão
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Cache simples (em produção, usar Redis)
        self._cache: Dict[str, tuple[Any, float]] = {}
        self.cache_ttl = int(os.getenv("CACHE_TTL", "300"))
        self.enable_cache = os.getenv("ENABLE_CACHE", "True").lower() == "true"
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Obtém valor do cache se ainda válido."""
        if not self.enable_cache:
            return None
        
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return value
            else:
                del self._cache[key]
        return None
    
    def _set_cache(self, key: str, value: Any) -> None:
        """Salva valor no cache."""
        if self.enable_cache:
            self._cache[key] = (value, time.time())
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError))
    )
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Faz requisição HTTP com retry logic.
        
        Args:
            method: Método HTTP (GET, POST, etc)
            endpoint: Endpoint da API
            data: Dados do body (JSON)
            params: Query parameters
        
        Returns:
            Response JSON
        
        Raises:
            APIError: Se a requisição falhar após retries
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params
                )
                
                # Verificar status
                if response.status_code >= 400:
                    raise APIError(
                        f"API error {response.status_code}: {response.text}"
                    )
                
                return response.json()
        
        except httpx.TimeoutException as e:
            raise APIError(f"Request timeout: {e}")
        except httpx.NetworkError as e:
            raise APIError(f"Network error: {e}")
        except Exception as e:
            raise APIError(f"Unexpected error: {e}")
    
    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """
        Busca cliente por ID.
        
        Args:
            customer_id: ID do cliente
        
        Returns:
            Customer object ou None se não encontrado
        """
        # Tentar cache primeiro
        cache_key = f"customer_{customer_id}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return Customer(**cached)
        
        try:
            data = self._request("GET", f"/customers/{customer_id}")
            customer = Customer(**data)
            self._set_cache(cache_key, data)
            return customer
        except APIError as e:
            print(f"⚠️  Erro ao buscar cliente: {e}")
            return None
    
    def search_customers(
        self,
        query: Optional[str] = None,
        email: Optional[str] = None,
        limit: int = 10
    ) -> List[Customer]:
        """
        Busca clientes por filtros.
        
        Args:
            query: Busca por nome ou empresa
            email: Filtrar por email
            limit: Número máximo de resultados
        
        Returns:
            Lista de Customer objects
        """
        params = {"limit": limit}
        if query:
            params["query"] = query
        if email:
            params["email"] = email
        
        try:
            data = self._request("GET", "/customers", params=params)
            return [Customer(**item) for item in data.get("customers", [])]
        except APIError as e:
            print(f"⚠️  Erro ao buscar clientes: {e}")
            return []
    
    def create_customer(
        self,
        name: str,
        email: str,
        phone: Optional[str] = None,
        company: Optional[str] = None
    ) -> Optional[Customer]:
        """
        Cria novo cliente.
        
        Args:
            name: Nome do cliente
            email: Email
            phone: Telefone (opcional)
            company: Empresa (opcional)
        
        Returns:
            Customer criado ou None se falhar
        """
        data = {
            "name": name,
            "email": email,
            "phone": phone,
            "company": company
        }
        
        try:
            response = self._request("POST", "/customers", data=data)
            return Customer(**response)
        except APIError as e:
            print(f"⚠️  Erro ao criar cliente: {e}")
            return None
    
    def get_deals(
        self,
        customer_id: Optional[str] = None,
        stage: Optional[str] = None
    ) -> List[Deal]:
        """
        Lista negociações.
        
        Args:
            customer_id: Filtrar por cliente (opcional)
            stage: Filtrar por estágio (opcional)
        
        Returns:
            Lista de Deal objects
        """
        params = {}
        if customer_id:
            params["customer_id"] = customer_id
        if stage:
            params["stage"] = stage
        
        try:
            data = self._request("GET", "/deals", params=params)
            return [Deal(**item) for item in data.get("deals", [])]
        except APIError as e:
            print(f"⚠️  Erro ao buscar deals: {e}")
            return []
    
    def create_deal(
        self,
        title: str,
        value: float,
        customer_id: str,
        stage: str = "qualification",
        probability: int = 10
    ) -> Optional[Deal]:
        """
        Cria nova negociação.
        
        Args:
            title: Título da negociação
            value: Valor estimado
            customer_id: ID do cliente
            stage: Estágio (qualification, proposal, negotiation, won, lost)
            probability: Probabilidade de ganhar (0-100)
        
        Returns:
            Deal criado ou None se falhar
        """
        data = {
            "title": title,
            "value": value,
            "customer_id": customer_id,
            "stage": stage,
            "probability": probability
        }
        
        try:
            response = self._request("POST", "/deals", data=data)
            return Deal(**response)
        except APIError as e:
            print(f"⚠️  Erro ao criar deal: {e}")
            return None
