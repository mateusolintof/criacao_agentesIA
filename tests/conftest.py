"""
Fixtures compartilhadas para testes.
"""

import pytest
from unittest.mock import Mock


@pytest.fixture
def mock_llm_client():
    """Mock do cliente LLM."""
    client = Mock()
    response = Mock()
    response.choices = [Mock()]
    response.choices[0].message.content = "Resposta simulada"
    response.usage.total_tokens = 100
    client.chat.completions.create.return_value = response
    return client


@pytest.fixture
def simple_memory():
    """Memória simples para testes."""
    class TestMemory:
        def __init__(self):
            self.data = {}

        def add(self, user_id, agent_id, interaction):
            key = f"{user_id}:{agent_id}"
            if key not in self.data:
                self.data[key] = {"messages": []}
            self.data[key]["messages"].append(interaction)

        def get(self, user_id, agent_id):
            key = f"{user_id}:{agent_id}"
            return self.data.get(key, {"messages": []})

    return TestMemory()


@pytest.fixture
def agent_config():
    """Configuração padrão para testes."""
    return {
        "model": "gpt-4-turbo-preview",
        "temperature": 0.7,
        "max_tokens": 500,
        "max_input_length": 2000
    }
