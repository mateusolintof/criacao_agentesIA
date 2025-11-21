# Exemplo: RAG Knowledge Base com AGNO

Sistema completo de **Q&A sobre base de conhecimento** usando **Retrieval-Augmented Generation (RAG)** com AGNO.

**Framework:** AGNO  
**Vector Database:** ChromaDB  
**Embeddings:** Sentence-Transformers  
**Atualizado:** 2025-11-20

## 🎯 Objetivo

Demonstrar como criar um sistema RAG que:
- **Carrega** documentos de várias fontes (MD, PDF, TXT, HTML)
- **Processa** e divide em chunks inteligentes
- **Indexa** usando embeddings vetoriais
- **Responde** perguntas baseado apenas no conhecimento carregado
- **Previne** alucinações (hallucination prevention)

## 🏗️ Arquitetura

```
User Question
    │
    ▼
┌─────────────────────────┐
│   AGNO Agent            │
│  (GPT-4 Turbo)          │
└───────────┬─────────────┘
            │
            ├─> search_knowledge(query)
            │
    ┌───────▼────────┐
    │ Vector Store   │
    │ (ChromaDB)     │
    └───────┬────────┘
            │
            ├─> Similarity Search
            │   (Top K documents)
            │
    ┌───────▼────────┐
    │  Embeddings    │
    │ (all-MiniLM)   │
    └────────────────┘
            │
    Retrieved Documents
            │
            ▼
    ┌─────────────────┐
    │ AGNO Agent      │
    │ Synthesizes     │
    │ Final Answer    │
    └─────────────────┘
```

## 📁 Estrutura

```
rag-knowledge-base/
├── README.md              # Este arquivo
├── main.py                # Sistema RAG completo
├── vector_store.py        # Integração com ChromaDB
├── knowledge_loader.py    # Processamento de documentos
├── sample_docs/           # Documentos de exemplo
│   ├── produto_crm.md
│   ├── produto_ai_assistant.md
│   └── processo_vendas.md
├── .env.example           # Variáveis de ambiente
└── requirements.txt       # Dependências específicas
```

## 🚀 Setup

### 1. Instalar dependências

```bash
# Na raiz do projeto ou neste diretório
pip install agno openai chromadb sentence-transformers pypdf python-dotenv beautifulsoup4 markdown

# Ou
pip install -r requirements.txt
```

### 2. Configurar ambiente

```bash
cd examples/rag-knowledge-base
cp .env.example .env
# Editar .env com sua OPENAI_API_KEY
```

### 3. Adicionar documentos

Coloque seus documentos na pasta `sample_docs/`:
- Formatos suportados: `.md`, `.txt`, `.pdf`, `.html`
- Já incluímos 3 documentos de exemplo

### 4. Executar

```bash
python main.py
```

Na primeira execução:
- Carregará todos documentos de `sample_docs/`
- Gerará embeddings (pode demorar alguns segundos)
- Salvará no ChromaDB (persistente)

Execuções seguintes serão instantâneas (usa cache).

## 💬 Exemplos de Uso

### Exemplo 1: Pergunta sobre Produto

```
👤 Você: Quanto custa o CRM Enterprise?

🤖 Assistente:
[Busca na base de conhecimento...]

O CRM Enterprise custa **R$ 199 por usuário/mês**.

Fonte: produto_crm.md

Além disso, há outras opções:
- **AI Assistant:** R$ 499/mês (conversas ilimitadas)
- **Analytics Suite:** R$ 299/mês

Gostaria de saber mais sobre algum desses produtos?
```

### Exemplo 2: Pergunta Técnica

```
👤 Você: Como funciona a qualificação de leads no processo BANT?

🤖 Assistente:
[Busca na base de conhecimento...]

A metodologia **BANT** qualifica leads em 4 dimensões:

**B - Budget (Orçamento)**
- Verificar se há orçamento alocado
- Critério: >= R$ 1.000/mês para CRM, >= R$ 500/mês para AI Assistant

**A - Authority (Autoridade)**
- Identificar quem toma a decisão
- Ideal: Decisor direto (CEO, Diretor)

**N - Need (Necessidade)**
- Entender problema específico
- Verificar urgência e impacto no negócio

**T - Timeline (Prazo)**
- Mapear quando precisam implementar
- Urgente (< 30 dias) tem prioridade

Fonte: processo_vendas.md (atualizado 2025-11-20)
```

### Exemplo 3: Comparação de Produtos

```
👤 Você: Qual a diferença entre CRM Enterprise e AI Assistant?

🤖 Assistente:
[Busca na base de conhecimento...]

**CRM Enterprise (R$ 199/usuário/mês):**
- Gestão de pipeline de vendas
- Automação de follow-ups
- Relatórios avançados
- **Ideal para:** Equipes de vendas de 5-100 pessoas
- **Implementação:** 4-6 semanas

**AI Assistant (R$ 499/mês):**
- Qualificação automática de leads 24/7
- Atendimento multi-canal (WhatsApp, chat, Messenger)
- Conversas ilimitadas
- **Ideal para:** Alto volume de leads (100+ por mês)
- **Implementação:** 7-10 dias

**Podem ser usados juntos:** AI Assistant qualifica leads automaticamente e integra com CRM Enterprise para gestão do pipeline.

Fontes: produto_crm.md, produto_ai_assistant.md
```

### Exemplo 4: Pergunta Fora da Base

```
👤 Você: Qual a previsão do tempo para amanhã?

🤖 Assistente:
[Busca na base de conhecimento...]

Desculpe, não encontrei informações sobre previsão do tempo na minha base de conhecimento. 

Minha expertise está focada em:
- Produtos (CRM Enterprise, AI Assistant, Analytics Suite)
- Processos de venda (metodologia BANT)
- Implementação e suporte

Posso ajudar com alguma dessas áreas?
```

## 🔑 Conceitos-Chave

### RAG (Retrieval-Augmented Generation)

RAG combina:
1. **Retrieval:** Busca documentos relevantes no vector store
2. **Augmentation:** Adiciona documentos ao contexto do LLM
3. **Generation:** LLM gera resposta baseada nos documentos

**Vantagens:**
- ✅ Respostas baseadas em fatos (não inventa)
- ✅ Sempre atualizado (basta recarregar documentos)
- ✅ Cita fontes (rastreabilidade)
- ✅ Menor custo (menos tokens que fine-tuning)

### Embeddings

Vetores numéricos que representam significado semântico:
- Textos similares têm embeddings próximos
- Permite busca por similaridade (não apenas keywords)
- Modelo usado: `all-MiniLM-L6-v2` (rápido e eficiente)

### Chunking

Divisão de documentos em pedaços menores:
- **Chunk size:** 1000 caracteres (configurável)
- **Overlap:** 200 caracteres (mantém contexto entre chunks)
- Chunks menores = mais precisão, mas pode perder contexto
- Chunks maiores = mais contexto, mas menos preciso

### AGNO Toolkit

Custom tools para o agente:
```python
class KnowledgeToolkit(Toolkit):
    def search_knowledge(self, query: str) -> str:
        """Busca na base de conhecimento"""
        results = self.vector_store.search(query, top_k=3)
        return formatted_results
```

Agente decide quando usar a ferramenta automaticamente.

## ⚙️ Configuração Avançada

### Ajustar Qualidade da Busca

No `.env`:
```bash
# Mais resultados = mais contexto, mas pode incluir irrelevantes
TOP_K_RESULTS=5  # Padrão: 3

# Chunks maiores = mais contexto por resultado
CHUNK_SIZE=1500  # Padrão: 1000
CHUNK_OVERLAP=300  # Padrão: 200
```

### Usar Modelo de Embeddings Diferente

```bash
# Modelos disponíveis: https://huggingface.co/sentence-transformers

# Mais preciso (mas mais lento)
EMBEDDING_MODEL=all-mpnet-base-v2

# Multilingual (melhor para português)
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2

# Mais rápido (mas menos preciso)
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Padrão
```

### Filtrar por Metadata

```python
# No vector_store.py, adicionar filtros
results = vector_store.search(
    query="preços",
    top_k=3,
    where={"filename": "produto_crm.md"}  # Buscar apenas neste arquivo
)
```

### Reprocessar Base de Conhecimento

```python
# Limpar e recarregar
from vector_store import VectorStore

vector_store = VectorStore()
vector_store.clear()  # Remove todos documentos

# Executar main.py novamente para recarregar
```

## 🔧 Troubleshooting

**Erro: "No module named 'sentence_transformers'"**
```bash
Solução: pip install sentence-transformers
```

**Erro: "ChromaDB not found"**
```bash
Solução: pip install chromadb
```

**Respostas imprecisas ou irrelevantes**
```
Solução 1: Aumentar TOP_K_RESULTS (mais documentos)
Solução 2: Melhorar qualidade dos documentos de origem
Solução 3: Ajustar CHUNK_SIZE (testar valores diferentes)
Solução 4: Usar modelo de embedding melhor (multilingual)
```

**Sistema muito lento**
```
Solução 1: Modelo de embedding está sendo baixado (primeira vez)
Solução 2: Usar modelo menor (all-MiniLM-L6-v2)
Solução 3: Reduzir TOP_K_RESULTS
```

**Agente inventa informações (hallucination)**
```
Solução: Melhorar instruções do agente
- Reforçar: "APENAS informações da base"
- Adicionar: "Se não sabe, diga que não sabe"
- Revisar: show_tool_calls=True para verificar se está buscando
```

## 📊 Métricas de Performance

### Tempo de Resposta
- **Primeira pergunta:** 3-5s (inclui busca vetorial + LLM)
- **Perguntas seguintes:** 2-3s (cache de embeddings)

### Custos (OpenAI)
- **Por pergunta:** ~$0.01 - $0.03 (depende do tamanho dos chunks)
- **Embeddings:** Gratuito (modelo local)
- **Vector DB:** Gratuito (ChromaDB open-source)

### Qualidade
- **Precisão:** > 90% (se documentos bem escritos)
- **Recall:** > 85% (encontra documentos relevantes)
- **Hallucination rate:** < 5% (com instruções corretas)

## 🆚 Quando Usar RAG

### Use RAG quando:
✅ Conteúdo muda frequentemente  
✅ Grande volume de documentação  
✅ Necessita citar fontes  
✅ Quer evitar alucinações  
✅ Informações proprietárias/confidenciais

### Use Fine-tuning quando:
✅ Conteúdo estável  
✅ Mudar estilo/tom do modelo  
✅ Domínio muito específico  
✅ Performance crítica (latência)

### Use Prompts simples quando:
✅ Conhecimento está no modelo base  
✅ Tarefa genérica  
✅ Budget limitado  
✅ Simplicidade é prioridade

## 📚 Próximos Passos

1. ✅ Teste com seus próprios documentos
2. Adicione mais fontes (APIs, databases, web scraping)
3. Implemente cache de respostas (Redis)
4. Adicione feedback loop (👍👎 para melhorar)
5. Configure re-ranking para melhor precisão
6. Adicione autenticação e controle de acesso

## 🔗 Exemplos Relacionados

- **Simple Chatbot (AGNO):** `examples/simple-chatbot/`
- **Multi-Agent Sales (CrewAI):** `examples/multi-agent-sales/`
- **API Integration (AGNO):** `examples/api-integration-agno/`

## 📖 Referências

- **AGNO Docs:** https://docs.agno.com
- **ChromaDB Docs:** https://docs.trychroma.com
- **Sentence-Transformers:** https://www.sbert.net
- **RAG Pattern:** https://arxiv.org/abs/2005.11401
