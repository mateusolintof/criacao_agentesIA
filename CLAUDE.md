# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Este é um template completo e metodologia padronizada para desenvolvimento de **Agentes de IA para Atendimento Comercial**. O framework fornece processos claros, templates reutilizáveis e guias práticos para criar soluções de qualidade em projetos de agentes conversacionais.

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

### Single-Agent vs Multi-Agent

**Single Agent**: Use para projetos simples com escopo limitado
- Mais fácil de implementar
- Adequado para 1-3 casos de uso

**Multi-Agent**: Use para projetos complexos
- Router Agent: Identifica intenção e roteia
- Specialized Agents: Sales, Support, Product, etc
- Melhor separação de responsabilidades
- Mais escalável

### Base Agent Pattern

Todos os agentes devem herdar de `BaseAgent`:
```python
from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def _load_prompts(self): ...
    def _initialize_tools(self): ...
    def process(self, user_input, context): ...
```

Ver `templates/agentes/base_agent.py` para referência completa.

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
Tipos de memória:
- **Short-term**: Contexto da conversa atual
- **Long-term**: Histórico e preferências
- Use ConversationBufferMemory para começar
- Evolua para Vector Memory se necessário

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
