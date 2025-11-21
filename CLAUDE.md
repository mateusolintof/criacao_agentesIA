# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Última atualização:** 2025-11-20

## Project Overview

Este é um template completo e metodologia padronizada para desenvolvimento de **Agentes de IA para Atendimento Comercial** usando **AGNO** (single-agent) e **CrewAI** (multi-agent). O framework fornece processos claros, templates reutilizáveis e guias práticos para criar soluções de qualidade em projetos de agentes conversacionais.

## Metodologia

A metodologia é composta por 6 processos principais:

1. **Descoberta e Planejamento**: Levantamento de requisitos, personas, jornadas
2. **Design da Solução**: Arquitetura de agentes, fluxos, prompts
3. **Desenvolvimento**: Implementação com qualidade e testes
4. **Validação e Ajustes**: Testes extensivos e otimização
5. **Deploy e Monitoramento**: Deploy seguro e observabilidade
6. **Melhoria Contínua**: Análise, otimização e evolução

Consulte `docs/metodologia/OVERVIEW.md` para visão completa.

## Architecture Patterns

### Framework Selection

**AGNO (Single-Agent)**: Use para projetos simples e focados
- Framework: `agno` >= 0.1.0
- Casos de uso: Chatbots diretos, RAG, assistentes especializados
- Adequado para: 1-3 casos de uso bem definidos
- Exemplos: `examples/simple-chatbot/`, `examples/rag-knowledge-base/`, `examples/api-integration-agno/`

**CrewAI (Multi-Agent)**: Use para projetos complexos com múltiplos domínios
- Framework: `crewai` >= 0.1.0
- Casos de uso: Equipes de agentes especializados, workflows complexos
- Adequado para: 4+ especialidades, delegação de tarefas
- Exemplos: `examples/multi-agent-sales/`

### AGNO Pattern (Single-Agent)

Agentes AGNO seguem este padrão:
```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb
from agno.tools.toolkit import Toolkit

# Criar agente
agent = Agent(
    name="Meu Agente",
    model=OpenAIChat(id="gpt-4-turbo"),
    db=SqliteDb(db_file="./data/memory.db"),
    instructions=["Instrução 1", "Instrução 2"],  # Lista de strings
    tools=[my_toolkit],
    add_history_to_context=True,
    num_history_runs=5
)

# Usar com sessão
response = agent.run(user_input, session_id="user123", stream=True)
```

Ver `templates/agentes/base_agent.py` e `examples/simple-chatbot/` para referência completa.

### CrewAI Pattern (Multi-Agent)

Sistemas multi-agente com CrewAI:
```python
from crewai import Agent, Task, Crew, Process, LLM

# Criar agentes especializados
manager = Agent(
    role="Manager",
    allow_delegation=True,  # Pode delegar
    llm=LLM(model="gpt-4-turbo")
)

specialist = Agent(
    role="Specialist",
    allow_delegation=False,  # Foca em especialidade
    llm=LLM(model="gpt-4-turbo")
)

# Criar crew com processo hierárquico
crew = Crew(
    agents=[manager, specialist],
    tasks=[task],
    process=Process.hierarchical,  # Manager coordena
    planning=True
)

result = crew.kickoff()
```

Ver `examples/multi-agent-sales/` para referência completa.

## Project Structure

```
/
├── docs/                    # Documentação
│   ├── metodologia/        # Metodologia completa
│   ├── processos/          # 6 processos detalhados
│   └── guias/              # Guias de implementação
├── templates/              # Templates reutilizáveis
│   ├── agentes/           # Templates de código
│   ├── fluxos/            # Templates de fluxos
│   ├── prompts/           # Templates de prompts
│   ├── planejamento/      # Templates de docs
│   └── integracao/        # Templates de API
├── examples/              # Exemplos de referência
├── src/                   # Código fonte (em projetos)
│   ├── agents/
│   ├── flows/
│   ├── integrations/
│   └── utils/
└── tests/                 # Testes (em projetos)
```

## Development Commands

### Setup de Novo Projeto
```bash
# Ver guia completo em docs/guias/quick-start.md

# Criar estrutura
mkdir projeto-cliente
cd projeto-cliente

# Copiar templates relevantes
cp -r ../templates/agentes src/agents/
cp ../templates/planejamento/escopo.md docs/

# Configurar ambiente
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Executar Testes
```bash
# Testes unitários
pytest tests/unit/ -v

# Testes de integração
pytest tests/integration/ -v

# Com coverage
pytest tests/ --cov=src --cov-report=term-missing

# Coverage mínimo esperado: 80%
```

### Validar Código
```bash
# Linting
pylint src/

# Formatação
black src/ tests/

# Type checking
mypy src/
```

## Key Concepts

### Prompts
- Use estrutura ROLE + CONTEXT + PERSONALITY + CONSTRAINTS + TASK + FORMAT
- Sempre versione prompts (v1.0, v1.1, etc)
- Template: `templates/prompts/template-prompt.md`
- Teste prompts antes de deploy

### Fluxos
- Mapeie como state machine
- Defina gatilhos de entrada/saída
- Planeje tratamento de erros e fallback
- Template: `templates/fluxos/template-fluxo.md`

### Guardrails
Sempre implemente:
- Input validation (tamanho, conteúdo malicioso)
- Output validation (informações sensíveis, compliance)
- Business rules (limites de desconto, autorizações)
- Hallucination detection

### Memory

**AGNO Memory Management:**
```python
from agno.db.sqlite import SqliteDb

# Memória persistente com SQLite
db = SqliteDb(
    session_table="conversations",
    db_file="./data/memory.db"
)

agent = Agent(
    db=db,
    add_history_to_context=True,  # Adiciona histórico ao contexto
    num_history_runs=5  # Últimas 5 interações
)

# Usar com session_id para contexto por usuário
response = agent.run(message, session_id="user_123")
```

**Tipos de memória:**
- **Short-term**: Contexto da conversa atual (num_history_runs)
- **Long-term**: Histórico persistente (SqliteDb ou PostgresDb)
- **Knowledge**: Base de conhecimento vetorial (ChromaDB para RAG)

**CrewAI Memory:**
- Usa memória automática entre agentes durante execução
- Para persistência, integrar com banco externo via custom tools

## Common Workflows

### Criar Novo Agente
1. Copiar `templates/agentes/base_agent.py`
2. Herdar de BaseAgent
3. Implementar métodos abstratos
4. Criar prompts em `templates/prompts/`
5. Adicionar testes em `tests/unit/`
6. Documentar em `docs/`

Ver: `docs/guias/criar-agente.md`

### Implementar Fluxo
1. Mapear estados e transições
2. Copiar `templates/fluxos/template-fluxo.md`
3. Implementar state machine
4. Adicionar validações
5. Testar casos edge
6. Criar diagrama mermaid

Ver: `docs/guias/implementar-fluxo.md`

### Integrar com API
1. Copiar `templates/integracao/template-spec-api.md`
2. Documentar especificação
3. Implementar client com retry logic
4. Adicionar caching
5. Implementar fallback
6. Testar error cases

Ver: `docs/guias/integracao-apis.md`

## Testing Standards

### Coverage Requirements
- Unit tests: >= 80%
- Integration tests: Todos os fluxos críticos
- E2E tests: Happy paths principais

### Test Structure
```python
def test_feature_name():
    """Descrição clara do que testa"""
    # Arrange
    agent = setup_agent()

    # Act
    result = agent.process(input)

    # Assert
    assert result["response"] is not None
```

### Conversation Tests
Criar dataset com:
- 50-100 conversas típicas
- 20-30 edge cases
- 10-20 casos de erro

Ver: `docs/guias/testes-conversacao.md`

## Deployment

### Pre-Deploy Checklist
- [ ] Todos testes passando
- [ ] Coverage >= 80%
- [ ] Security scan sem issues críticos
- [ ] Documentação atualizada
- [ ] Runbook de operação pronto
- [ ] Monitoramento configurado
- [ ] Rollback plan definido

### Deploy Strategy
Use **Canary Deployment**:
1. Deploy para 5% do tráfego
2. Monitorar por 2-4h
3. Aumentar para 25% se estável
4. Aumentar para 50%
5. Completar para 100%

Ver: `docs/processos/05-deploy-monitoramento.md`

## Monitoring

### Métricas Essenciais

**Técnicas**:
- Response time p95 < 2s
- Error rate < 1%
- Uptime >= 99.5%

**Negócio**:
- Taxa de conversão
- CSAT >= 4.0
- Volume de leads

**IA**:
- Intent accuracy >= 90%
- Hallucination rate < 5%
- Token usage e custos

### Dashboards
Templates em: `templates/monitoramento/dashboards.json`

### Alertas
Configuração em: `templates/monitoramento/alertas.yaml`
- P0 (Crítico): Resposta em 15min
- P1 (Alto): Resposta em 2h
- P2 (Médio): Revisão diária

## Cost Optimization

### LLM Costs
- Use modelos menores para tasks simples
- Implemente aggressive caching
- Otimize prompts (menos tokens)
- Use function calling vs generation

### Infrastructure
- Auto-scaling apropriado
- Reserved instances
- Otimizar queries de banco

Target: Custo por conversa < R$ 10

## Documentation Requirements

Cada projeto deve ter:
- [ ] `docs/escopo.md` - Escopo completo
- [ ] `docs/arquitetura.md` - Arquitetura e decisões
- [ ] `docs/fluxos/` - Todos os fluxos mapeados
- [ ] `docs/operacao/runbook.md` - Runbook de operação
- [ ] `README.md` - Setup e instruções
- [ ] Código com docstrings

## Quick Reference

**Iniciar novo projeto**: `docs/guias/quick-start.md`
**Processos completos**: `docs/processos/README.md`
**Templates**: `templates/README.md`
**Metodologia**: `docs/metodologia/OVERVIEW.md`

## Best Practices

1. **Sempre valide inputs e outputs** (guardrails)
2. **Versione prompts** e documente mudanças
3. **Teste antes de deploy** (coverage >= 80%)
4. **Monitore em produção** (métricas + alertas)
5. **Documente decisões** (ADRs)
6. **Itere baseado em dados** (A/B testing)
7. **Mantenha custos sob controle** (otimize continuamente)

## Support

- Metodologia: `docs/metodologia/OVERVIEW.md`
- Troubleshooting: `docs/guias/troubleshooting.md`
- Templates: `templates/README.md`

Para questões específicas, consulte os processos e guias detalhados na pasta `docs/`.
