# Quick Start - Criar Novo Projeto de Agentes de IA

Este guia mostra como iniciar rapidamente um novo projeto seguindo a metodologia.

## Pré-requisitos

- [ ] Acesso ao repositório
- [ ] Python 3.9+ ou Node.js 18+ instalado
- [ ] Git configurado
- [ ] Acesso a provider de LLM (OpenAI, Anthropic, etc)
- [ ] Cliente aprovou projeto

## Passo 1: Criar Estrutura do Projeto

```bash
# Clone este template
git clone [URL_DESTE_TEMPLATE] meu-novo-projeto
cd meu-novo-projeto

# Remova git history do template
rm -rf .git
git init

# Crie estrutura específica do projeto
mkdir -p {
  projeto-cliente/docs/{requisitos,jornadas,personas},
  projeto-cliente/src/{agents,flows,integrations,utils},
  projeto-cliente/tests/{unit,integration,e2e},
  projeto-cliente/config
}
```

## Passo 2: Documentar Requisitos

```bash
# Copie e preencha templates
cp templates/planejamento/escopo.md projeto-cliente/docs/escopo.md
cp templates/planejamento/requisitos.md projeto-cliente/docs/requisitos.md

# Edite com informações do cliente
# code projeto-cliente/docs/escopo.md
```

**O que documentar**:
- Objetivos de negócio
- Personas
- Casos de uso principais
- Integrações necessárias
- Métricas de sucesso

Referência: [Processo 01 - Descoberta e Planejamento](../processos/01-descoberta-planejamento.md)

## Passo 3: Desenhar Arquitetura

```bash
# Crie documento de arquitetura
cp templates/arquitetura/template.md projeto-cliente/docs/arquitetura.md
```

**Decisões importantes**:
- Single-agent vs Multi-agent
- LLM provider (OpenAI, Anthropic, etc)
- Vector database (Pinecone, Weaviate, etc)
- Framework (LangChain, LlamaIndex, etc)

Referência: [Processo 02 - Design da Solução](../processos/02-design-solucao.md)

## Passo 4: Configurar Ambiente

### Python

```bash
cd projeto-cliente

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
cat > requirements.txt << EOF
langchain==0.1.0
openai==1.0.0
pinecone-client==3.0.0
python-dotenv==1.0.0
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.0
pytest==7.4.0
EOF

pip install -r requirements.txt
```

### Configurar Secrets

```bash
# Criar arquivo .env
cat > .env << EOF
# LLM
OPENAI_API_KEY=sk-...
# ou
ANTHROPIC_API_KEY=sk-...

# Vector DB
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=...

# Integrações
CRM_API_KEY=...
CRM_API_URL=...

# Config
ENVIRONMENT=development
LOG_LEVEL=INFO
EOF

# Adicionar ao .gitignore
echo ".env" >> .gitignore
```

## Passo 5: Criar Primeiro Agente

```bash
# Copiar template de agente
cp ../../templates/agentes/base_agent.py src/agents/
```

Criar agente específico:

```python
# src/agents/sales_agent.py
from agents.base_agent import BaseAgent

class SalesAgent(BaseAgent):
    """Agente especializado em vendas"""

    def _load_prompts(self):
        return {
            "system": """
            Você é um consultor de vendas especializado.
            Seu objetivo é ajudar clientes a encontrar
            a melhor solução para suas necessidades.

            Seja consultivo, não apenas venda.
            """,
            "greeting": "Olá! Como posso ajudar você hoje?",
        }

    def _initialize_tools(self):
        return []  # Adicionar tools depois

    def process(self, user_input, context):
        # Validar input
        is_valid, error = self.validate_input(user_input)
        if not is_valid:
            return {"error": error}

        # Processar com LLM
        response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.prompts["system"]},
                {"role": "user", "content": user_input}
            ]
        )

        agent_response = response.choices[0].message.content

        # Aplicar guardrails
        safe_response, passed = self.apply_guardrails(
            agent_response,
            context
        )

        # Log interaction
        self.log_interaction(
            user_input,
            safe_response,
            context,
            success=passed
        )

        return {
            "response": safe_response,
            "metadata": {
                "tokens_used": response.usage.total_tokens
            }
        }
```

## Passo 6: Criar Primeiro Fluxo

```bash
# Copiar template de fluxo
cp ../../templates/fluxos/template-fluxo.md docs/fluxos/qualificacao-lead.md
```

Implementar fluxo básico:

```python
# src/flows/lead_qualification.py
class LeadQualificationFlow:
    """Fluxo de qualificação de lead"""

    def __init__(self, agent):
        self.agent = agent
        self.state = "greeting"
        self.collected_data = {}

    def process_message(self, user_message, context):
        if self.state == "greeting":
            return self._handle_greeting(user_message)

        elif self.state == "collect_info":
            return self._collect_info(user_message)

        elif self.state == "qualify":
            return self._qualify_lead(user_message)

    def _handle_greeting(self, message):
        self.state = "collect_info"
        return {
            "response": "Olá! Para te ajudar melhor, preciso entender suas necessidades. Qual sua principal dor?",
            "state": self.state
        }

    # ... implementar outros estados
```

## Passo 7: Testes Básicos

```python
# tests/unit/test_sales_agent.py
import pytest
from agents.sales_agent import SalesAgent

def test_sales_agent_greeting():
    """Testa saudação do agente"""
    agent = SalesAgent(
        agent_id="test_sales",
        config={},
        llm_client=mock_llm,
        memory=mock_memory
    )

    result = agent.process("Olá", {})
    assert "response" in result
    assert len(result["response"]) > 0

def test_input_validation():
    """Testa validação de input"""
    agent = SalesAgent(...)

    # Input vazio
    is_valid, error = agent.validate_input("")
    assert not is_valid

    # Input muito longo
    is_valid, error = agent.validate_input("a" * 3000)
    assert not is_valid

    # Input válido
    is_valid, error = agent.validate_input("Olá")
    assert is_valid
```

Executar testes:

```bash
pytest tests/ -v
```

## Passo 8: Executar Localmente

```python
# main.py
from agents.sales_agent import SalesAgent
from dotenv import load_dotenv
import openai

load_dotenv()

# Inicializar agente
agent = SalesAgent(
    agent_id="sales_001",
    config={"max_input_length": 2000},
    llm_client=openai,
    memory={}  # Implementar depois
)

# Testar interação
while True:
    user_input = input("Você: ")
    if user_input.lower() in ['sair', 'exit', 'quit']:
        break

    result = agent.process(user_input, {})
    print(f"Agente: {result['response']}\n")
```

Executar:

```bash
python main.py
```

## Passo 9: Configurar CI/CD

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          pytest tests/ --cov=src --cov-report=term-missing
```

## Passo 10: Documentar Projeto

```bash
# Criar README específico do projeto
cat > projeto-cliente/README.md << EOF
# Projeto [NOME]

## Descrição
[BREVE DESCRIÇÃO]

## Setup
\`\`\`bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env com suas chaves
\`\`\`

## Executar
\`\`\`bash
python main.py
\`\`\`

## Testes
\`\`\`bash
pytest tests/
\`\`\`

## Documentação
- [Escopo](docs/escopo.md)
- [Arquitetura](docs/arquitetura.md)
- [Fluxos](docs/fluxos/)

## Contato
- Tech Lead: [NOME]
- Email: [EMAIL]
EOF
```

## Próximos Passos

Agora que você tem o básico funcionando:

1. **Expandir funcionalidades**
   - Adicionar mais agentes
   - Implementar fluxos complexos
   - Integrar com APIs

2. **Melhorar qualidade**
   - Adicionar mais testes
   - Implementar guardrails
   - Configurar knowledge base

3. **Preparar para produção**
   - Configurar monitoramento
   - Setup de deploy
   - Documentação de operação

## Referências

- [Metodologia Completa](../metodologia/OVERVIEW.md)
- [Processos Detalhados](../processos/README.md)
- [Templates](../../templates/README.md)

## Troubleshooting

### Erro: "Module not found"
```bash
# Certifique-se que venv está ativado
source venv/bin/activate
pip install -r requirements.txt
```

### Erro: "API key not found"
```bash
# Verifique .env
cat .env | grep API_KEY
# Certifique-se que python-dotenv está instalado
```

### Erro: Testes falhando
```bash
# Execute com mais verbosidade
pytest tests/ -v -s
# Verifique mocks
```
