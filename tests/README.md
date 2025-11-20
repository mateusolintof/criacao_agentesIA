# Testes

Este diretório contém exemplos de testes para o framework de Agentes de IA.

## Estrutura

```
tests/
├── README.md              # Este arquivo
├── conftest.py            # Fixtures do pytest
├── unit/                  # Testes unitários
│   ├── test_base_agent.py
│   ├── test_validators.py
│   └── test_utils.py
├── integration/           # Testes de integração
│   ├── test_llm_integration.py
│   ├── test_crm_integration.py
│   └── test_memory.py
└── e2e/                   # Testes end-to-end
    └── test_conversation_flows.py
```

## Executar Testes

```bash
# Todos os testes
pytest tests/

# Apenas unitários
pytest tests/unit/ -v

# Apenas integração
pytest tests/integration/ -v

# Com coverage
pytest tests/ --cov=src --cov-report=term-missing

# Específico
pytest tests/unit/test_validators.py -v
```

## Exemplos Disponíveis

- `unit/test_validators.py` - Validação de inputs
- `integration/test_llm_integration.py` - Integração com LLM
- `e2e/test_conversation_flows.py` - Fluxos completos de conversa
