# Exemplos de Implementação

Este diretório contém exemplos práticos e completos de como usar o framework para construir agentes de IA.

## 📁 Exemplos Disponíveis

### 1. Simple Chatbot (`simple-chatbot/`)
**Nível:** Iniciante
**Tempo:** 15 minutos

Um chatbot simples com um único agente para demonstrar os conceitos básicos.

**O que você vai aprender:**
- Estrutura básica de um agente
- Configuração de prompts
- Loop de conversação
- Memória básica

**Execute:**
```bash
cd simple-chatbot
cp .env.example .env
# Editar .env com sua OPENAI_API_KEY
python main.py
```

---

### 2. Multi-Agent Sales (`multi-agent-sales/`)
**Nível:** Intermediário
**Tempo:** 30 minutos

Sistema multi-agente com router que direciona para agentes especializados.

**O que você vai aprender:**
- Arquitetura multi-agente
- Router pattern
- Agentes especializados
- Handoff entre agentes

**Agentes incluídos:**
- Router Agent: Identifica intenção e roteia
- Sales Agent: Especialista em vendas
- Support Agent: Especialista em suporte

---

### 3. API Integration (`api-integration/`)
**Nível:** Intermediário
**Tempo:** 30 minutos

Agente integrado com CRM externo (exemplo com mock API).

**O que você vai aprender:**
- Integração com APIs externas
- Retry logic e circuit breaker
- Fallback strategies
- Error handling robusto

**Inclui:**
- Cliente CRM com retry
- Agente que cria leads automaticamente
- Simulação de falhas de API

---

### 4. RAG Knowledge Base (`rag-knowledge-base/`)
**Nível:** Avançado
**Tempo:** 45 minutos

Agente com base de conhecimento usando RAG (Retrieval-Augmented Generation).

**O que você vai aprender:**
- Implementação de RAG
- Vector stores (ChromaDB/FAISS)
- Embeddings
- Busca semântica

**Inclui:**
- Loader de documentos
- Vector store setup
- Agente com retrieval
- Documentos de exemplo

---

## 🚀 Como Usar Este Diretório

### Pré-requisitos

1. **Python 3.11+** instalado
2. **API Key** da OpenAI (ou outro provedor LLM)
3. **Dependências** instaladas:

```bash
# Na raiz do projeto
pip install -r requirements.txt
```

### Ordem Recomendada de Aprendizado

```
1. simple-chatbot/          ← Comece aqui
   ↓
2. multi-agent-sales/       ← Arquitetura escalável
   ↓
3. api-integration/         ← Integração com sistemas
   ↓
4. rag-knowledge-base/      ← Base de conhecimento
```

### Estrutura Padrão dos Exemplos

Cada exemplo segue esta estrutura:

```
example-name/
├── README.md          # Documentação específica
├── main.py            # Ponto de entrada
├── .env.example       # Template de variáveis de ambiente
├── requirements.txt   # Dependências específicas (se houver)
└── ...                # Arquivos específicos do exemplo
```

---

## 💡 Dicas

### Para Iniciantes

1. **Comece pelo simple-chatbot**
   - É o mais simples e direto
   - Introduz conceitos fundamentais
   - Executa em minutos

2. **Leia o código comentado**
   - Todos os exemplos têm comentários explicativos
   - Entenda cada seção antes de modificar

3. **Experimente modificações**
   - Mude os prompts
   - Ajuste configurações
   - Adicione novas funcionalidades

### Para Desenvolvedores Experientes

1. **Use como base para seus projetos**
   - Copie a estrutura que faz sentido
   - Adapte para seu caso de uso
   - Mantenha boas práticas

2. **Combine padrões**
   - Multi-agent + API Integration
   - RAG + Multi-agent
   - Custom combinations

3. **Otimize para produção**
   - Adicione logging robusto
   - Implemente monitoring
   - Configure CI/CD

---

## 📚 Recursos Adicionais

### Documentação

- **Metodologia completa:** `/docs/metodologia/OVERVIEW.md`
- **Processos detalhados:** `/docs/processos/`
- **Guias práticos:** `/docs/guias/`

### Templates

- **Agentes:** `/templates/agentes/`
- **Prompts:** `/templates/prompts/`
- **Fluxos:** `/templates/fluxos/`
- **Integrações:** `/templates/integracao/`

### Referências

- **Base Agent:** `/templates/agentes/base_agent.py`
- **Sales Agent Example:** `/templates/agentes/sales_agent.py`

---

## 🔧 Troubleshooting

### Erro: "Module not found"

```bash
# Certifique-se de estar no diretório correto
cd Python_Structure

# Instale as dependências
pip install -r requirements.txt
```

### Erro: "OpenAI API Key not configured"

```bash
# Copie o .env.example
cp .env.example .env

# Edite o .env e adicione sua chave
# OPENAI_API_KEY=sk-your-key-here
```

### Agente não responde adequadamente

1. Verifique os prompts (geralmente em `prompts.py`)
2. Ajuste a temperatura (mais baixo = mais determinístico)
3. Aumente max_tokens se respostas estão cortadas

### Performance lenta

1. Use modelo mais rápido (gpt-3.5-turbo)
2. Reduza histórico de conversação
3. Implemente caching de respostas

---

## 🤝 Contribuindo

Quer adicionar um novo exemplo?

1. Crie um novo diretório com nome descritivo
2. Siga a estrutura padrão dos exemplos
3. Adicione README.md completo
4. Comente o código extensivamente
5. Teste completamente antes de commit

---

## 📞 Suporte

- **Issues:** Problemas técnicos
- **Discussions:** Perguntas e ideias
- **Guia de Troubleshooting:** `/docs/guias/troubleshooting.md`

---

## 🎯 Próximos Passos

Depois de explorar os exemplos:

1. ✅ Escolha um exemplo como base
2. ✅ Adapte para seu caso de uso
3. ✅ Siga o processo de desenvolvimento (veja `/docs/processos/`)
4. ✅ Implemente testes (veja `/docs/guias/testes-conversacao.md`)
5. ✅ Deploy em produção (veja `/docs/guias/deploy.md`)

Bom desenvolvimento! 🚀
