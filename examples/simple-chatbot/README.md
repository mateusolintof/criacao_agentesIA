# Exemplo: Simple Chatbot com AGNO

Este é um exemplo simples de um chatbot de atendimento usando o framework **AGNO** com um único agente.

## O que este exemplo demonstra

- Implementação básica de agente único com AGNO
- Memória persistente com SQLite
- Configuração de instruções (prompts no formato AGNO)
- Loop interativo de chat
- Validação de inputs e guardrails
- Estatísticas de uso

## Estrutura

```
simple-chatbot/
├── README.md          # Este arquivo
├── main.py            # Ponto de entrada com AGNO Agent
├── agent_config.py    # Configuração do agente
├── prompts.py         # Instruções no formato AGNO (lista)
├── simple_memory.py   # Implementação de memória (referência)
├── .env.example       # Exemplo de variáveis de ambiente
└── requirements.txt   # Dependências específicas
```

## Setup

### 1. Instalar dependências

```bash
# Na raiz do projeto Python_Structure
pip install -r requirements.txt

# Ou apenas as dependências essenciais do AGNO
pip install agno openai python-dotenv
```

### 2. Configurar variáveis de ambiente

```bash
# Copiar exemplo (se não existir)
cp .env.example .env

# Editar .env e adicionar sua OPENAI_API_KEY
# Exemplo:
# OPENAI_API_KEY=sk-...
```

### 3. Executar

```bash
cd examples/simple-chatbot
python main.py
```

## Como usar

1. O chatbot inicia e apresenta uma mensagem de boas-vindas
2. Digite suas mensagens no prompt
3. O agente AGNO responde mantendo o contexto da conversa (memória persistente)
4. Digite 'sair' ou 'quit' para encerrar e ver estatísticas

## Exemplo de interação

```
==============================================================
  CHATBOT SIMPLES - AGNO Framework
==============================================================

Digite suas mensagens e pressione Enter.
Para sair, digite 'sair' ou 'quit'.

Você: Olá, quero conhecer seus produtos
Agente: Olá! Ficamos felizes em apresentar nossos produtos.
Temos 3 soluções principais:

1. CRM Enterprise (R$ 199/mês) - Gestão completa de vendas
2. AI Assistant (R$ 499/mês) - Automação inteligente
3. Analytics Suite (R$ 299/mês) - Business Intelligence

Qual deles te interessa mais?

Você: Me fale sobre o AI Assistant
Agente: O AI Assistant é nossa plataforma de automação com IA
generativa. Por R$ 499/mês você tem acesso a automações
inteligentes para seu negócio. Posso te dar mais detalhes?

Você: sair

Encerrando conversa. Até logo!

Estatísticas da sessão:
   - Mensagens: 2
   - Taxa de sucesso: 100.0%
   - Tempo médio: 1.45s
```

## Arquitetura AGNO

Este exemplo usa o padrão moderno do AGNO:

```python
# 1. Criar agente com memória
agent = Agent(
    name="simple_chatbot",
    model=OpenAIChat(id="gpt-4o"),
    instructions=[...],  # Lista de instruções
    storage=SqliteDb(...),  # Memória persistente
    add_history_to_messages=True,  # Contexto histórico
    num_history_messages=10
)

# 2. Executar com session_id
response = agent.run(
    message,
    session_id=session_id,
    stream=False
)
```

## Personalização

### Mudar o comportamento do agente

Edite `prompts.py` para modificar as instruções:
- Role e contexto
- Produtos e preços
- Personalidade e tom
- Constraints e regras

```python
PROMPTS = {
    "instructions": [
        "Você é um assistente...",
        "Seja amigável mas profissional",
        # Adicione suas instruções
    ]
}
```

### Mudar modelo LLM

Edite `agent_config.py`:

```python
AGENT_CONFIG = {
    "model": "gpt-4o",  # ou "gpt-4-turbo", "gpt-3.5-turbo"
    "num_history_messages": 10,
    # ...
}
```

### Adicionar ferramentas (tools)

Veja o exemplo `api-integration-agno/` para aprender a criar e usar ferramentas AGNO.

## Próximos passos

1. **Comece aqui** - Entenda o básico do AGNO com este exemplo
2. **Multi-Agent** - Veja `multi-agent-sales/` para sistemas com múltiplos agentes (CrewAI)
3. **RAG** - Explore `rag-knowledge-base/` para base de conhecimento com busca semântica
4. **API Integration** - Veja `api-integration-agno/` para conectar com APIs externas

## Conceitos AGNO

### Memória Persistente
- Usa SQLite por padrão (desenvolvimento)
- Troque para PostgreSQL em produção
- Mantém histórico entre sessões
- Session ID identifica cada conversa

### Instruções (Instructions)
- Lista de strings ao invés de prompt único
- Mais modular e fácil de versionar
- Cada item é uma regra ou contexto

### Guardrails
- Validação de input (tamanho, conteúdo malicioso)
- Validação de output (informações sensíveis)
- Implementado no wrapper SimpleChatbot

## Troubleshooting

**Erro: OPENAI_API_KEY não configurada**
```bash
# Configure no arquivo .env
echo "OPENAI_API_KEY=sk-your-key" > .env
```

**Erro: Module 'agno' not found**
```bash
pip install agno
```

**Agente não mantém contexto**
```
Verifique se está usando o mesmo session_id nas chamadas
```

**Banco de dados com erro**
```bash
# Remova o banco e deixe ser recriado
rm /tmp/simple_chatbot.db
```

## Diferenças da versão anterior

Esta versão migrada usa AGNO framework:

| Aspecto | Versão Antiga | Versão AGNO |
|---------|---------------|-------------|
| Framework | BaseAgent customizado | AGNO nativo |
| Memória | SimpleMemory (dict) | SqliteDb (persistente) |
| Prompts | String única | Lista de instruções |
| LLM | OpenAI client direto | OpenAIChat (wrapper) |
| Session | user_id + context | session_id |

## Recursos adicionais

- [Documentação AGNO](https://docs.agno.com)
- [AGNO GitHub](https://github.com/agno/agno)
- Template base: `templates/agentes/base_agent.py`
- Metodologia: `docs/metodologia/OVERVIEW.md`
