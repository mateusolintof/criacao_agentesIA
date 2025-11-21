# Exemplo: Simple Chatbot com AGNO

Este é um exemplo simples de um chatbot de atendimento usando **AGNO** (framework de agentes single-agent).

**Atualizado:** 2025-11-20

## O que este exemplo demonstra

- ✅ Implementação básica com AGNO Agent
- ✅ Memória persistente com SQLite
- ✅ Contexto de conversação mantido automaticamente
- ✅ Loop interativo de chat
- ✅ Streaming de respostas
- ✅ Configuração via variáveis de ambiente

## Estrutura

```
simple-chatbot/
├── README.md          # Este arquivo
├── main.py            # Ponto de entrada com AGNO
├── .env.example       # Exemplo de variáveis de ambiente
└── tmp/               # Criado automaticamente para memória SQLite
```

## Setup

### 1. Instalar dependências

```bash
# Na raiz do projeto Python_Structure
pip install agno openai python-dotenv

# Ou instalar tudo
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

```bash
cd examples/simple-chatbot
cp .env.example .env
# Editar .env e adicionar sua OPENAI_API_KEY
```

### 3. Executar

```bash
python main.py
```

## Como usar

1. O chatbot inicia e apresenta uma mensagem de boas-vindas
2. Digite suas mensagens no prompt
3. O agente responde mantendo o contexto da conversa
4. Digite 'sair' ou 'quit' para encerrar

## Exemplo de interação

```
🤖  CHATBOT SIMPLES - AGNO Framework
============================================================

Digite suas mensagens e pressione Enter.
Para sair, digite 'sair' ou 'quit'.

👤 Você: Olá, quero saber sobre seus produtos
🤖 Agente: Olá! Temos 3 produtos principais:
- CRM Enterprise (R$ 199/mês) - Gestão completa de vendas
- AI Assistant (R$ 499/mês) - Automação inteligente
- Analytics Suite (R$ 299/mês) - Business Intelligence

Qual deles te interessa mais?

👤 Você: Quanto custa o CRM?
🤖 Agente: O CRM Enterprise custa R$ 199 por usuário/mês e inclui gestão de pipeline, automação de follow-ups e relatórios em tempo real. Quantos usuários você tem no time?

👤 Você: sair
👋 Encerrando conversa. Até logo!
```

## Principais recursos do AGNO

### Memória Persistente
- Usa SQLite para armazenar histórico
- Mantém contexto entre reinicializações
- Configurável via `num_history_runs`

### Streaming
- Respostas aparecem em tempo real
- Melhor experiência do usuário
- Ativado com `stream=True`

### Session Management
- Cada usuário tem seu próprio `session_id`
- Conversas isoladas por sessão
- Histórico mantido automaticamente

## Personalização

### Mudar o comportamento do agente

Edite a lista `instructions` em `main.py`:

```python
instructions = [
    "Você é um [PERSONALIDADE]",
    "Seus produtos são: [LISTAR]",
    "Seja sempre [COMPORTAMENTO]",
]
```

### Ajustar memória

```python
agent = Agent(
    ...
    num_history_runs=10,  # Mais contexto
    add_history_to_context=True,
)
```

### Mudar modelo

No `.env`:
```bash
OPENAI_MODEL=gpt-4o  # ou gpt-4o-mini, gpt-4-turbo
```

## Arquitetura AGNO

```
User Input
    │
    ▼
Agent.run(input, session_id)
    │
    ├─> Recupera histórico do SQLite
    ├─> Adiciona instruções
    ├─> Envia para LLM (OpenAI)
    ├─> Salva no SQLite
    │
    ▼
Response (streaming)
```

## Próximos passos

1. ✅ Explore este exemplo simples
2. Veja `multi-agent-sales/` para sistema com **CrewAI**
3. Veja `rag-knowledge-base/` para **RAG com AGNO**
4. Veja `api-integration-agno/` para **integrações com APIs**

## Troubleshooting

**Erro: OpenAI API Key não configurada**
```
Solução: Configure OPENAI_API_KEY no arquivo .env
```

**Erro: Module 'agno' not found**
```
Solução: Execute pip install agno
```

**Agente não lembra conversa anterior**
```
Solução: Verifique se o session_id está sendo passado corretamente
```

**Respostas muito longas**
```
Solução: Ajuste max_tokens no OpenAIChat ou refine as instruções
```

## Comparação: Antes vs Agora

### Antes (LangChain)
```python
from langchain import ConversationChain
chain = ConversationChain(...)
response = chain.run(input)
```

### Agora (AGNO)
```python
from agno.agent import Agent
agent = Agent(...)
response = agent.run(input, session_id="user-123")
```

**Vantagens do AGNO:**
- 🚀 Mais simples e direto
- 💾 Memória SQLite built-in
- 🔧 Menos dependências
- ⚡ Mais rápido e leve
- 📊 Melhor para produção

## Referências

- **Documentação AGNO:** https://docs.agno.ai
- **Exemplo avançado:** `templates/agentes/sales_agent.py`
- **Multi-agent:** `examples/multi-agent-sales/` (CrewAI)
