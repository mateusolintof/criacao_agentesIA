# Template de Agentes de IA para Atendimento Comercial

> Metodologia completa e padronizada para desenvolvimento de soluções de Agentes de IA focadas em atendimento comercial usando **AGNO** e **CrewAI**.

**Última atualização:** 2025-11-20

## 🎯 Visão Geral

Este repositório fornece um framework completo para criar Agentes de IA para atendimento comercial, incluindo:

- **Metodologia estruturada** em 6 processos claros
- **Frameworks modernos** (AGNO para single-agent, CrewAI para multi-agent)
- **Templates reutilizáveis** para documentação e código
- **Exemplos práticos** funcionais e testados
- **Guias práticos** de implementação
- **Padrões de arquitetura** testados e validados

## ⚙️ Requisitos do Sistema

### Python Version (IMPORTANTE!)

**Este projeto requer Python 3.10, 3.11 ou 3.12**

```bash
# Verificar sua versão
python --version

# ✅ Versões suportadas:
# Python 3.12.x (RECOMENDADO)
# Python 3.11.x
# Python 3.10.x

# ❌ NÃO suportado:
# Python 3.13+ (ChromaDB e CrewAI ainda não suportam)
# Python 3.9 ou anterior
```

**Se você tem Python 3.13+**, siga o guia de instalação: [`docs/guias/python-version-setup.md`](docs/guias/python-version-setup.md)

### Outras Dependências

- Git
- pip >= 21.0
- Conexão com internet (para instalar pacotes)
- 4GB+ RAM recomendado
- 2GB+ espaço em disco

## 📋 O Que Você Encontra Aqui

### Documentação
```
docs/
├── metodologia/     # Metodologia completa e princípios
├── processos/       # 6 processos detalhados (Descoberta → Melhoria Contínua)
└── guias/          # Guias práticos de implementação
```

### Templates
```
templates/
├── agentes/        # Templates de código para agentes
├── fluxos/         # Templates de fluxos conversacionais
├── prompts/        # Templates de prompts
├── planejamento/   # Templates de documentação
└── integracao/     # Templates de integração
```

## 🚀 Quick Start

### Método 1: Setup Automatizado (Recomendado)

```bash
# 1. Clone o repositório
git clone [URL_DESTE_REPO] meu-projeto-agentes
cd meu-projeto-agentes

# 2. Execute o script de setup (verifica Python, cria venv, instala tudo)
./scripts/setup-environment.sh

# 3. Edite suas API keys
nano .env

# 4. Pronto! Teste um exemplo
cd examples/simple-chatbot
python main.py
```

### Método 2: Setup Manual

#### 1. Clone e Configure Ambiente
```bash
# Clone
git clone [URL_DESTE_REPO] meu-projeto-agentes
cd meu-projeto-agentes

# Verifique Python version (DEVE ser 3.10-3.12)
python --version

# Crie ambiente virtual
python -m venv venv

# Ative
source venv/bin/activate  # macOS/Linux
# ou
.\venv\Scripts\activate  # Windows

# Atualize pip
pip install --upgrade pip

# Instale dependências
pip install -r requirements.txt
```

#### 2. Configure Variáveis de Ambiente
```bash
# Copie o exemplo
cp .env.example .env

# Edite e adicione suas API keys
nano .env  # ou use seu editor favorito
```

#### 3. Leia a Metodologia
```bash
# Visão geral
cat docs/metodologia/OVERVIEW.md

# Processos detalhados
ls docs/processos/
```

### 3. Inicie Novo Projeto
```bash
# Siga o guia de início rápido
cat docs/guias/quick-start.md
```

## 📚 Metodologia - 6 Processos

### 1. Descoberta e Planejamento
- Levantamento de requisitos
- Mapeamento de jornadas
- Definição de personas
- Análise de integrações

[Ver processo completo →](docs/processos/01-descoberta-planejamento.md)

### 2. Design da Solução
- Arquitetura de agentes
- Design de fluxos conversacionais
- Definição de prompts
- Estratégia de knowledge base

[Ver processo completo →](docs/processos/02-design-solucao.md)

### 3. Desenvolvimento
- Implementação de agentes
- Desenvolvimento de fluxos
- Integração com sistemas
- Testes e documentação

[Ver processo completo →](docs/processos/03-desenvolvimento.md)

### 4. Validação e Ajustes
- Testes de conversação
- Validação com stakeholders
- Ajuste de prompts
- Otimização de fluxos

[Ver processo completo →](docs/processos/04-validacao-ajustes.md)

### 5. Deploy e Monitoramento
- Deploy seguro (Canary)
- Configuração de monitoramento
- Setup de alertas
- Treinamento de equipe

[Ver processo completo →](docs/processos/05-deploy-monitoramento.md)

### 6. Melhoria Contínua
- Análise de métricas
- Otimização de prompts
- A/B testing
- Evolução de funcionalidades

[Ver processo completo →](docs/processos/06-melhoria-continua.md)

## 🏗️ Padrões de Arquitetura

### AGNO (Single-Agent)
Para projetos simples e focados (1-3 casos de uso)
```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb

agent = Agent(
    name="Sales Agent",
    model=OpenAIChat(id="gpt-4-turbo"),
    db=SqliteDb(db_file="./data/memory.db"),
    instructions=["Você é um consultor de vendas...", "..."],
    tools=[crm_toolkit],
    add_history_to_context=True
)

response = agent.run(user_input, session_id="user_123", stream=True)
```

**Exemplos:** `simple-chatbot/`, `rag-knowledge-base/`, `api-integration-agno/`

### CrewAI (Multi-Agent)
Para projetos complexos com múltiplas especialidades
```python
from crewai import Agent, Task, Crew, Process, LLM

# Manager coordena especialistas
manager = Agent(role="Manager", allow_delegation=True, ...)
sales = Agent(role="Sales", allow_delegation=False, ...)
support = Agent(role="Support", allow_delegation=False, ...)

crew = Crew(
    agents=[manager, sales, support],
    tasks=[task],
    process=Process.hierarchical,  # Manager coordena
    planning=True
)

result = crew.kickoff()
```

**Exemplo:** `multi-agent-sales/`

[Ver guia de arquitetura →](docs/guias/criar-agente.md)

## 📦 Templates Principais

### Código
- [`base_agent.py`](templates/agentes/base_agent.py) - Classe base para agentes
- [`template-fluxo.md`](templates/fluxos/template-fluxo.md) - Mapeamento de fluxos
- [`template-prompt.md`](templates/prompts/template-prompt.md) - Estrutura de prompts

### Documentação
- [`escopo.md`](templates/planejamento/escopo.md) - Documento de escopo
- [`requisitos.md`](templates/planejamento/requisitos.md) - Levantamento de requisitos
- [`template-spec-api.md`](templates/integracao/template-spec-api.md) - Especificação de APIs

## 🎓 Guias Práticos

- [Quick Start](docs/guias/quick-start.md) - Iniciar novo projeto
- [Criar Agente](docs/guias/criar-agente.md) - Como criar novo agente
- [Implementar Fluxo](docs/guias/implementar-fluxo.md) - Como implementar fluxos
- [Integração com APIs](docs/guias/integracao-apis.md) - Como integrar sistemas
- [Testes](docs/guias/testes-conversacao.md) - Como testar conversações

## ✅ Melhores Práticas

### Prompts
- Use estrutura: ROLE + CONTEXT + PERSONALITY + CONSTRAINTS + TASK + FORMAT
- Sempre versione (v1.0, v1.1, etc)
- Teste antes de deploy
- Documente mudanças

### Fluxos
- Mapeie como state machine
- Planeje tratamento de erros
- Defina estratégias de fallback
- Teste casos edge

### Guardrails
- Input validation (tamanho, conteúdo malicioso)
- Output validation (informações sensíveis)
- Business rules (limites, autorizações)
- Hallucination detection

### Testes
- Coverage >= 80%
- Testes de conversação extensivos
- Validação com usuários reais
- Performance testing

### Monitoramento
- Response time p95 < 2s
- Error rate < 1%
- CSAT >= 4.0
- Intent accuracy >= 90%

## 📊 Métricas de Sucesso

### Técnicas
- Uptime >= 99.5%
- Response time p95 < 2s
- Error rate < 1%
- Intent accuracy >= 90%

### Negócio
- Taxa de conversão
- Volume de leads
- Ticket médio
- ROI do projeto

### Qualidade
- CSAT >= 4.0
- Taxa de resolução no 1º contato
- Taxa de escalação para humano
- Satisfação da equipe

## 💰 Otimização de Custos

### LLM
- Use modelos menores para tasks simples
- Implemente caching agressivo
- Otimize prompts (menos tokens)
- Use function calling

### Infraestrutura
- Auto-scaling apropriado
- Reserved instances
- Otimize queries

**Target**: Custo por conversa < R$ 10

## 🛠️ Stack Tecnológica Recomendada

### AI Agent Frameworks
- **AGNO** >= 0.1.0: Single-agent systems (chatbots, RAG, API integration)
- **CrewAI** >= 0.1.0: Multi-agent orchestration (teams, hierarchical workflows)

### LLM Providers
- **OpenAI** (GPT-4 Turbo, GPT-4o, GPT-4o-mini) - Recomendado
- Anthropic (Claude Sonnet, Opus)
- Open source (Llama 3, Mistral)

### Vector Databases (para RAG)
- **ChromaDB**: Open-source, fácil de usar (recomendado para MVP)
- Pinecone: Managed, escalável
- Weaviate: Open-source, completo
- Qdrant: Performance otimizado

### Memory & Storage
- **SqliteDb** (AGNO): Desenvolvimento e MVPs
- PostgresDb (AGNO): Produção
- Redis: Caching e sessions

### Monitoramento
- Prometheus + Grafana (métricas)
- OpenTelemetry (traces)
- DataDog / New Relic (APM)

## 💡 Exemplos Práticos

### 1. Simple Chatbot (AGNO)
Chatbot comercial básico com memória persistente.
```bash
cd examples/simple-chatbot
python main.py
```
**Features:** Memória de conversação, streaming, session management

### 2. Multi-Agent Sales (CrewAI)
Sistema com 4 agentes especializados (Manager, Sales, Support, Product).
```bash
cd examples/multi-agent-sales
python main.py
```
**Features:** Processo hierárquico, delegação, planejamento automático

### 3. RAG Knowledge Base (AGNO)
Sistema Q&A sobre base de conhecimento com RAG.
```bash
cd examples/rag-knowledge-base
python main.py
```
**Features:** ChromaDB, embeddings, chunking, hallucination prevention

### 4. API Integration (AGNO)
Integração com APIs externas (CRM) com retry logic.
```bash
cd examples/api-integration-agno
python main.py
```
**Features:** Retry logic, caching, error handling, Pydantic validation

## 📖 Documentação Adicional

- [CLAUDE.md](CLAUDE.md) - Guia para Claude Code
- [Metodologia Completa](docs/metodologia/OVERVIEW.md)
- [Processos Detalhados](docs/processos/README.md)
- [Templates](templates/README.md)

## 🤝 Como Usar em Projetos

### Opção 1: Copiar Template
```bash
cp -r templates/agentes seu-projeto/src/agents/
cp templates/planejamento/escopo.md seu-projeto/docs/
```

### Opção 2: Seguir Metodologia
1. Leia a metodologia completa
2. Execute cada processo sequencialmente
3. Use templates como base
4. Adapte para seu contexto

### Opção 3: Quick Start
```bash
# Siga o guia de início rápido
cat docs/guias/quick-start.md
```

## 📝 Exemplo de Uso

### Com AGNO (Single-Agent)

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb
from agno.tools.toolkit import Toolkit

# Criar custom toolkit
class CRMToolkit(Toolkit):
    def __init__(self):
        super().__init__(name="crm_toolkit")
        self.register(self.search_customer)
        self.register(self.create_deal)

    def search_customer(self, email: str) -> str:
        """Busca cliente por email no CRM"""
        # Lógica de integração
        return f"Cliente encontrado: {email}"

    def create_deal(self, customer_id: str, value: float) -> str:
        """Cria nova negociação"""
        # Lógica de criação
        return f"Deal criado: R$ {value}"

# Configurar agente
agent = Agent(
    name="Agente Comercial",
    model=OpenAIChat(id="gpt-4-turbo"),
    db=SqliteDb(db_file="./data/memory.db"),
    instructions=[
        "Você é um consultor de vendas B2B",
        "Use metodologia BANT para qualificação",
        "Sempre busque no CRM antes de criar novo cliente"
    ],
    tools=[CRMToolkit()],
    add_history_to_context=True,
    num_history_runs=5
)

# Usar
response = agent.run(
    "Quero comprar um CRM para 50 pessoas",
    session_id="user_123",
    stream=True
)
```

### Com CrewAI (Multi-Agent)

```python
from crewai import Agent, Task, Crew, Process, LLM

# Agente Manager
manager = Agent(
    role="Gerente Comercial",
    goal="Coordenar equipe de vendas",
    backstory="Gerente experiente...",
    allow_delegation=True,
    llm=LLM(model="gpt-4-turbo")
)

# Agente Vendedor
sales = Agent(
    role="Consultor de Vendas",
    goal="Qualificar e fechar negócios",
    backstory="Especialista em BANT...",
    allow_delegation=False,
    llm=LLM(model="gpt-4-turbo")
)

# Tarefa
task = Task(
    description="Atender cliente interessado em CRM",
    expected_output="Proposta comercial completa",
    agent=manager
)

# Crew
crew = Crew(
    agents=[manager, sales],
    tasks=[task],
    process=Process.hierarchical
)

result = crew.kickoff()
```

## 🎯 Casos de Uso

Esta metodologia é ideal para:
- ✅ Qualificação de leads
- ✅ Atendimento comercial 24/7
- ✅ Apresentação de produtos
- ✅ Geração de orçamentos
- ✅ Agendamento de reuniões
- ✅ Follow-up automatizado
- ✅ Upsell e cross-sell

## ⚠️ Avisos Importantes

1. **LGPD**: Sempre implemente proteções de dados pessoais
2. **Custos**: Monitore uso de tokens e APIs
3. **Testes**: Nunca pule fase de validação
4. **Monitoramento**: Essencial em produção
5. **Documentação**: Mantenha sempre atualizada

## 📞 Suporte

Para dúvidas sobre a metodologia:
1. Consulte [docs/metodologia/OVERVIEW.md](docs/metodologia/OVERVIEW.md)
2. Revise os processos em [docs/processos/](docs/processos/)
3. Consulte os guias em [docs/guias/](docs/guias/)

## 📄 Licença

[Adicione sua licença aqui]

## 🙏 Contribuindo

Contribuições são bem-vindas! Se você:
- Melhorou um processo
- Criou um novo template útil
- Encontrou um padrão que funciona bem
- Tem sugestões de melhoria

Por favor, documente e compartilhe.

---

**Desenvolvido para criar Agentes de IA de alta qualidade para Atendimento Comercial** 🤖💼
