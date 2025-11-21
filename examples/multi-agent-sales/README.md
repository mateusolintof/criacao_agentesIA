# Exemplo: Sistema Multi-Agente com CrewAI

Sistema completo de atendimento comercial com **4 agentes especializados** trabalhando em equipe usando **CrewAI** com processo hierárquico.

**Framework:** CrewAI  
**Processo:** Hierarchical (Manager coordena especialistas)  
**Atualizado:** 2025-11-20

## 🎯 Objetivo

Demonstrar como criar um sistema multi-agente onde:
- Um **Manager** analisa a necessidade e coordena
- **Especialistas** (Vendas, Suporte, Produto) focam em suas áreas
- Agentes **colaboram** através de delegação
- Sistema **escalável** e fácil de expandir

## 👥 Equipe de Agentes

### 1. Gerente de Atendimento (Manager)
- **Papel:** Coordenar a equipe
- **Responsabilidade:** Analisar necessidade e delegar para especialista correto
- **Delegação:** ✅ Sim (coordena todos)

### 2. Consultor de Vendas
- **Papel:** Qualificação e vendas
- **Metodologia:** BANT (Budget, Authority, Need, Timeline)
- **Delegação:** ❌ Não (foca em vendas)

### 3. Especialista em Suporte
- **Papel:** Ajuda técnica
- **Responsabilidade:** Resolver dúvidas técnicas e troubleshooting
- **Delegação:** ❌ Não (foca em suporte)

### 4. Especialista em Produtos
- **Papel:** Informações detalhadas
- **Responsabilidade:** Funcionalidades, casos de uso, comparações
- **Delegação:** ❌ Não (foca em produtos)

## 📁 Estrutura

```
multi-agent-sales/
├── README.md          # Este arquivo
├── main.py            # Sistema completo com CrewAI
├── .env.example       # Variáveis de ambiente
└── requirements.txt   # Dependências específicas
```

## 🚀 Setup

### 1. Instalar dependências

```bash
# Na raiz do projeto
pip install crewai crewai[tools] openai python-dotenv

# Ou
pip install -r requirements.txt
```

### 2. Configurar ambiente

```bash
cd examples/multi-agent-sales
cp .env.example .env
# Editar .env com sua OPENAI_API_KEY
```

### 3. Executar

```bash
python main.py
```

## 💬 Exemplos de Uso

### Exemplo 1: Pergunta sobre Vendas

```
👤 Você: Quero comprar um CRM para minha empresa de 50 pessoas

🤖 Sistema:
[Manager analisa → Delega para Consultor de Vendas]

Consultor de Vendas: Excelente! Para te ajudar melhor, posso fazer 
algumas perguntas?
1. Qual seu orçamento mensal para essa solução?
2. Você é o decisor ou precisa de aprovação?
3. Qual o principal desafio que precisa resolver?
4. Qual o prazo para implementação?

(Sistema qualifica e apresenta solução adequada)
```

### Exemplo 2: Dúvida Técnica

```
👤 Você: Como configuro integração do CRM com WhatsApp?

🤖 Sistema:
[Manager analisa → Delega para Especialista em Suporte]

Especialista em Suporte: Para configurar a integração WhatsApp:

1. Acesse Configurações > Integrações
2. Selecione "WhatsApp Business API"
3. Insira seu Business Account ID
4. Configure webhooks...

(Resposta técnica detalhada com passo-a-passo)
```

### Exemplo 3: Comparação de Produtos

```
👤 Você: Qual a diferença entre CRM Enterprise e AI Assistant?

🤖 Sistema:
[Manager analisa → Delega para Especialista em Produtos]

Especialista em Produtos:
CRM Enterprise vs AI Assistant:

CRM Enterprise (R$ 199/usuário):
- Gestão de pipeline de vendas
- Automação de follow-ups
- Relatórios avançados
- Ideal para: Equipes de vendas estruturadas

AI Assistant (R$ 499/mês):
- Qualificação automática 24/7
- Atendimento multi-canal
- Integração com CRM
- Ideal para: Alto volume de leads

(Comparação detalhada com casos de uso)
```

## 🏗️ Arquitetura CrewAI

```
User Input
    │
    ▼
┌─────────────────────────┐
│   Manager Agent         │
│  (Hierarchical Leader)  │
└───────────┬─────────────┘
            │
            ├─ Analisa necessidade
            ├─ Planeja abordagem
            └─ Delega para especialista
            │
    ┌───────┼────────┬──────────┐
    ▼       ▼        ▼          ▼
┌────────┐ ┌──────┐ ┌────────┐ ┌─────────┐
│ Sales  │ │Support│ │Product │ │ (Outro) │
│ Agent  │ │ Agent │ │ Agent  │ │  Agent  │
└────────┘ └──────┘ └────────┘ └─────────┘
    │
    └─> Especialista executa
        └─> Retorna para Manager
            └─> Manager entrega resultado final
```

## 🔑 Conceitos-Chave do CrewAI

### Process.hierarchical
- **Manager** automaticamente criado
- Coordena e delega tarefas
- Garante qualidade e completude

### allow_delegation
- **True:** Pode delegar para outros agentes
- **False:** Foca apenas em sua especialidade

### Task
- Describe claramente o objetivo
- Define expected_output
- Atribui ao agente responsável

### Crew
- Agrupa agentes e tarefas
- Define processo (sequential ou hierarchical)
- Executa via `kickoff()`

## ⚙️ Configuração Avançada

### Usar modelos diferentes por agente

```python
# Manager usa modelo premium
manager = Agent(
    role="Manager",
    llm=LLM(model="gpt-4o"),  # Mais inteligente
    ...
)

# Especialistas usam modelo eficiente
sales = Agent(
    role="Sales",
    llm=LLM(model="gpt-4o-mini"),  # Mais barato
    ...
)
```

### Adicionar ferramentas customizadas

```python
from crewai_tools import tool

@tool
def search_crm(customer_email: str) -> dict:
    """Busca cliente no CRM"""
    # Implementação...
    return customer_data

sales_agent = Agent(
    role="Sales",
    tools=[search_crm],
    ...
)
```

### Planning Mode

```python
crew = Crew(
    ...
    planning=True,  # Manager planeja antes de executar
    planning_llm="gpt-4-turbo",  # Modelo para planejamento
)
```

## 🆚 Quando Usar Multi-Agent vs Single-Agent

### Use Multi-Agent (CrewAI) quando:
✅ Múltiplos domínios de conhecimento  
✅ Necessita especialização  
✅ Workflows complexos  
✅ Delegação de tarefas  
✅ 4+ casos de uso diferentes

### Use Single-Agent (AGNO) quando:
✅ Escopo focado  
✅ 1-3 casos de uso  
✅ Simplicidade é prioridade  
✅ Menor overhead  
✅ Chatbot direto

## 🔧 Troubleshooting

**Erro: "No OpenAI API key found"**
```
Solução: Configure OPENAI_API_KEY no .env
```

**Agentes não estão delegando**
```
Solução: Verifique allow_delegation=True no manager
```

**Respostas muito longas**
```
Solução: Seja mais específico na descrição da Task
```

**Manager não escolhe agente certo**
```
Solução: Melhore o backstory dos agentes para diferenciar especialidades
```

## 📚 Próximos Passos

1. ✅ Teste com diferentes tipos de perguntas
2. Adicione mais agentes especializados
3. Implemente ferramentas customizadas (CRM, DB, APIs)
4. Configure memória persistente
5. Adicione validações e guardrails

## 🔗 Exemplos Relacionados

- **Simple Chatbot (AGNO):** `examples/simple-chatbot/`
- **RAG Knowledge Base (AGNO):** `examples/rag-knowledge-base/`
- **API Integration (AGNO):** `examples/api-integration-agno/`

## 📖 Referências

- **CrewAI Docs:** https://docs.crewai.com
- **Hierarchical Process:** https://docs.crewai.com/concepts/processes#hierarchical
- **Agent Collaboration:** https://docs.crewai.com/concepts/collaboration
