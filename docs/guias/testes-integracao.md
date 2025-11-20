# Guia: Testes de Integração

## Visão Geral

Testes de integração verificam que componentes funcionam corretamente juntos: agente + API, agente + database, fluxo completo, etc.

## Setup de Testes

```python
# tests/integration/conftest.py
import pytest
from integrations.crm_client import CRMClient
from database import get_db
import os

@pytest.fixture(scope="session")
def test_database():
    """Database de teste."""
    # Usar database de teste
    os.environ["DATABASE_URL"] = "postgresql://localhost/test_db"

    # Setup
    db = get_db()
    db.create_all()

    yield db

    # Teardown
    db.drop_all()


@pytest.fixture
def crm_client():
    """CRM client para testes."""
    # Usar API de staging ou mock server
    return CRMClient(
        api_key=os.getenv("CRM_TEST_API_KEY"),
        base_url="https://staging.crm.com/api"
    )
```

## Testes de API

```python
# tests/integration/test_crm_integration.py
import pytest

def test_create_lead_integration(crm_client):
    """Testa criação de lead real."""
    lead_data = {
        "company_name": f"Test Corp {datetime.now().timestamp()}",
        "contact_name": "Test User",
        "email": f"test_{datetime.now().timestamp()}@test.com",
        "phone": "11999999999"
    }

    result = crm_client.create_lead(lead_data)

    # Verificar sucesso
    assert result["success"] is True
    assert "lead_id" in result

    # Verificar que lead foi criado (buscar)
    lead = crm_client.get_lead(result["lead_id"])
    assert lead is not None
    assert lead["company_name"] == lead_data["company_name"]

    # Cleanup
    crm_client.delete_lead(result["lead_id"])


def test_api_error_handling(crm_client):
    """Testa tratamento de erro da API."""
    # Dados inválidos
    invalid_data = {"invalid": "data"}

    result = crm_client.create_lead(invalid_data)

    # Deve retornar erro estruturado
    assert result["success"] is False
    assert "error" in result
```

## Testes de Fluxo Completo

```python
# tests/integration/test_full_flow.py
def test_qualification_flow_with_crm(agent, flow, crm_client, test_database):
    """Testa fluxo completo: coleta + qualificação + CRM."""
    context = {"user_id": "integration_test_user"}

    # Simular conversação
    messages = [
        "Olá",
        "Empresa Test, 100 funcionários",
        "Precisamos de CRM",
        "R$ 3000/mês",
        "Urgente",
        "Sou o diretor"
    ]

    for message in messages:
        result = flow.process_message(message, context)
        assert result.get("error") is None

    # Verificar que lead foi criado no CRM
    leads = crm_client.search_leads({"company": "Empresa Test"})
    assert len(leads) > 0

    # Verificar dados no database
    conversation = test_database.conversations.find_one({"user_id": context["user_id"]})
    assert conversation is not None
    assert conversation["qualification_score"] >= 70
```

## Testes com Mock Server

```python
# tests/integration/test_with_mock_server.py
from unittest.mock import patch
import responses

@responses.activate
def test_crm_with_mock():
    """Testa integração com CRM mockado."""
    # Mock da API
    responses.add(
        responses.POST,
        "https://api.crm.com/leads",
        json={"id": "mock_lead_123", "status": "created"},
        status=201
    )

    # Testar
    client = CRMClient(api_key="test_key", base_url="https://api.crm.com")
    result = client.create_lead({"company": "Test"})

    assert result["success"] is True
    assert result["lead_id"] == "mock_lead_123"
```

## Testes Assíncronos

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_flow():
    """Testa fluxo assíncrono."""
    agent = AsyncAgent(...)

    tasks = [
        agent.process("message 1", {}),
        agent.process("message 2", {}),
        agent.process("message 3", {})
    ]

    results = await asyncio.gather(*tasks)

    assert all(r["success"] for r in results)
```

## Database Integration Tests

```python
def test_conversation_persistence(test_database):
    """Testa persistência de conversas."""
    # Criar conversa
    conversation = {
        "user_id": "test_123",
        "messages": [
            {"role": "user", "content": "Olá"},
            {"role": "agent", "content": "Como posso ajudar?"}
        ],
        "created_at": datetime.utcnow()
    }

    # Salvar
    conv_id = test_database.conversations.insert_one(conversation).inserted_id

    # Recuperar
    retrieved = test_database.conversations.find_one({"_id": conv_id})

    assert retrieved is not None
    assert len(retrieved["messages"]) == 2
    assert retrieved["user_id"] == "test_123"
```

## Próximos Passos

- [Testes de Performance](testes-performance.md)
- [Deploy](deploy.md)

## Referências

- [Pytest Integration Testing](https://docs.pytest.org/en/stable/how-to/integration.html)
