# Guia: Knowledge Base e RAG (Retrieval-Augmented Generation)

## Visão Geral

RAG permite que agentes acessem conhecimento específico do domínio, documentos e dados atualizados. Este guia ensina como implementar knowledge bases usando vector databases e retrieval semântico.

## Quando Usar RAG

**Use RAG para**:
- Documentação de produtos (specs técnicas, manuais)
- Políticas e procedimentos da empresa
- Catálogos extensos (produtos, serviços)
- FAQs e conhecimento de suporte
- Dados que mudam frequentemente

**Não use RAG para**:
- Conhecimento geral (LLM já sabe)
- Dados estruturados simples (use banco de dados)
- Informações que cabem no prompt

## Arquitetura RAG

```
User Query → Embedding → Vector Search → Retrieve Docs → LLM + Context → Response
```

## Setup Rápido

### 1. Instalar Dependências

```bash
pip install langchain chromadb sentence-transformers openai pinecone-client
```

### 2. Escolher Vector Database

**ChromaDB** (Local, fácil para dev):
```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("knowledge_base")
```

**Pinecone** (Produção, escalável):
```python
import pinecone

pinecone.init(api_key="...", environment="us-west1-gcp")
index = pinecone.Index("knowledge-base")
```

### 3. Implementação Básica

```python
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

# Carregar documentos
loader = DirectoryLoader("data/docs/", glob="**/*.md")
documents = loader.load()

# Dividir em chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = text_splitter.split_documents(documents)

# Criar embeddings e armazenar
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(chunks, embeddings)

# Buscar conhecimento relevante
def get_relevant_context(query: str, k: int = 3):
    """Busca top-k documentos relevantes."""
    results = vectorstore.similarity_search(query, k=k)
    return "\n\n".join([doc.page_content for doc in results])

# Usar com LLM
query = "Como configurar o produto X?"
context = get_relevant_context(query)

prompt = f"""
Baseado neste contexto:
{context}

Responda: {query}
"""
```

## Estratégias de Chunking

### Tamanho de Chunk

```python
# Pequeno (200-500 tokens): Respostas precisas, pode perder contexto
splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)

# Médio (500-1000 tokens): Balanço ideal para maioria dos casos
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)

# Grande (1000-2000 tokens): Mais contexto, pode ter informação irrelevante
splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=300)
```

### Overlap

```python
# Overlap garante que informações não sejam cortadas
# Regra: 15-25% do chunk_size
chunk_size = 1000
chunk_overlap = 200  # 20%
```

### Por Estrutura de Documento

```python
# Markdown: Separar por seções
from langchain.text_splitter import MarkdownTextSplitter
splitter = MarkdownTextSplitter(chunk_size=1000)

# Código: Separar por funções/classes
from langchain.text_splitter import PythonCodeTextSplitter
splitter = PythonCodeTextSplitter(chunk_size=1000)
```

## Metadata e Filtragem

```python
# Adicionar metadata aos chunks
documents = [
    Document(
        page_content=content,
        metadata={
            "source": "produto_x_manual.pdf",
            "category": "technical",
            "version": "2.0",
            "last_updated": "2025-11-20"
        }
    )
]

# Buscar com filtros
results = vectorstore.similarity_search(
    "configuração",
    k=5,
    filter={"category": "technical", "version": "2.0"}
)
```

## Embeddings

### Modelos de Embedding

```python
# OpenAI (melhor qualidade, pago)
from langchain.embeddings import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

# Sentence Transformers (gratuito, local)
from langchain.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Cohere (alternativa)
from langchain.embeddings import CohereEmbeddings
embeddings = CohereEmbeddings(model="embed-multilingual-v2.0")
```

### Multilíngue

```python
# Para português
embeddings = HuggingFaceEmbeddings(
    model_name="neuralmind/bert-base-portuguese-cased"
)
```

## Implementação Completa

```python
# src/knowledge/rag_engine.py
"""
RAG Engine para knowledge base.
"""

from typing import List, Dict, Any
import logging
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import DirectoryLoader, PDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


class RAGEngine:
    """
    Engine de RAG para busca semântica em knowledge base.
    """

    def __init__(
        self,
        vector_store_path: str = "./data/vectorstore",
        embedding_model: str = "text-embedding-ada-002",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.logger = logging.getLogger(__name__)

        # Embeddings
        self.embeddings = OpenAIEmbeddings(model=embedding_model)

        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

        # Vector store
        self.vectorstore = Chroma(
            persist_directory=vector_store_path,
            embedding_function=self.embeddings
        )

        self.logger.info("RAG Engine initialized")

    def index_documents(self, docs_path: str, glob_pattern: str = "**/*"):
        """
        Indexa documentos na knowledge base.

        Args:
            docs_path: Caminho para documentos
            glob_pattern: Padrão de arquivos
        """
        # Carregar documentos
        loader = DirectoryLoader(docs_path, glob=glob_pattern)
        documents = loader.load()

        self.logger.info(f"Loaded {len(documents)} documents")

        # Dividir em chunks
        chunks = self.text_splitter.split_documents(documents)

        self.logger.info(f"Created {len(chunks)} chunks")

        # Adicionar ao vector store
        self.vectorstore.add_documents(chunks)
        self.vectorstore.persist()

        self.logger.info("Documents indexed successfully")

        return len(chunks)

    def search(
        self,
        query: str,
        k: int = 3,
        filter_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca documentos relevantes.

        Args:
            query: Query de busca
            k: Número de resultados
            filter_metadata: Filtros de metadata

        Returns:
            Lista de documentos relevantes com scores
        """
        # Buscar com scores
        results = self.vectorstore.similarity_search_with_score(
            query,
            k=k,
            filter=filter_metadata
        )

        # Formatar resultados
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            })

        return formatted_results

    def get_context_for_query(
        self,
        query: str,
        k: int = 3,
        min_score: float = 0.7
    ) -> str:
        """
        Retorna contexto formatado para usar com LLM.

        Args:
            query: Query
            k: Top-k resultados
            min_score: Score mínimo

        Returns:
            Contexto concatenado
        """
        results = self.search(query, k=k)

        # Filtrar por score
        relevant_results = [
            r for r in results
            if r["score"] >= min_score
        ]

        if not relevant_results:
            self.logger.warning(f"No relevant results for: {query}")
            return ""

        # Concatenar conteúdos
        context_parts = []
        for i, result in enumerate(relevant_results, 1):
            source = result["metadata"].get("source", "Unknown")
            content = result["content"]

            context_parts.append(f"""
            [Documento {i} - {source}]
            {content}
            """)

        return "\n\n".join(context_parts)


# Uso com agente
class RAGAgent:
    """Agente com acesso a knowledge base via RAG."""

    def __init__(self, llm, rag_engine: RAGEngine):
        self.llm = llm
        self.rag = rag_engine

    def process(self, query: str) -> str:
        """
        Processa query usando RAG.

        Args:
            query: Pergunta do usuário

        Returns:
            Resposta baseada em knowledge base
        """
        # Buscar contexto relevante
        context = self.rag.get_context_for_query(query, k=3)

        if not context:
            return "Desculpe, não encontrei informações sobre isso na base de conhecimento."

        # Criar prompt com contexto
        prompt = f"""
        Baseado APENAS nas informações abaixo, responda a pergunta do usuário.
        Se a informação não estiver disponível, diga que não sabe.

        INFORMAÇÕES:
        {context}

        PERGUNTA: {query}

        RESPOSTA:
        """

        # Chamar LLM
        response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3  # Mais factual
        )

        return response.choices[0].message.content
```

## Otimizações

### Hybrid Search (Keyword + Semantic)

```python
from langchain.retrievers import BM25Retriever, EnsembleRetriever

# Retriever semântico
semantic_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# Retriever por keywords
bm25_retriever = BM25Retriever.from_documents(documents)

# Combinar ambos
ensemble_retriever = EnsembleRetriever(
    retrievers=[semantic_retriever, bm25_retriever],
    weights=[0.7, 0.3]  # 70% semântico, 30% keyword
)
```

### Re-ranking

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank_results(query: str, results: List):
    """Re-ranqueia resultados usando cross-encoder."""
    pairs = [[query, r["content"]] for r in results]
    scores = reranker.predict(pairs)

    # Ordenar por novo score
    for i, score in enumerate(scores):
        results[i]["rerank_score"] = score

    return sorted(results, key=lambda x: x["rerank_score"], reverse=True)
```

### Caching

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def get_cached_context(query_hash: str):
    """Cache de buscas."""
    return cached_results.get(query_hash)

def search_with_cache(query: str):
    query_hash = hashlib.md5(query.encode()).hexdigest()

    cached = get_cached_context(query_hash)
    if cached:
        return cached

    results = rag.search(query)
    cached_results[query_hash] = results
    return results
```

## Atualização da Knowledge Base

```python
def update_knowledge_base():
    """Atualiza knowledge base com novos documentos."""
    # 1. Detectar novos/modificados documentos
    new_docs = detect_new_documents()

    # 2. Remover documentos antigos (se necessário)
    for old_doc in get_outdated_documents():
        vectorstore.delete(filter={"source": old_doc})

    # 3. Indexar novos documentos
    rag_engine.index_documents(new_docs)

    # 4. Persistir
    vectorstore.persist()

    logger.info(f"Knowledge base updated: {len(new_docs)} new documents")

# Agendar atualização automática
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(update_knowledge_base, 'cron', hour=2)  # 2 AM diariamente
scheduler.start()
```

## Métricas e Avaliação

```python
def evaluate_rag_quality(test_queries: List[Dict]):
    """
    Avalia qualidade do RAG.

    Args:
        test_queries: [{"query": "...", "expected_doc": "..."}, ...]
    """
    metrics = {
        "recall_at_3": [],
        "mrr": [],  # Mean Reciprocal Rank
        "avg_score": []
    }

    for test in test_queries:
        query = test["query"]
        expected_doc = test["expected_doc"]

        # Buscar
        results = rag.search(query, k=3)

        # Recall@3
        found = any(expected_doc in r["metadata"]["source"] for r in results)
        metrics["recall_at_3"].append(1 if found else 0)

        # MRR
        for i, r in enumerate(results):
            if expected_doc in r["metadata"]["source"]:
                metrics["mrr"].append(1 / (i + 1))
                break
        else:
            metrics["mrr"].append(0)

        # Average score
        metrics["avg_score"].append(np.mean([r["score"] for r in results]))

    return {
        "recall@3": np.mean(metrics["recall_at_3"]),
        "mrr": np.mean(metrics["mrr"]),
        "avg_score": np.mean(metrics["avg_score"])
    }
```

## Troubleshooting

### Resultados irrelevantes

**Soluções**:
```python
# 1. Ajustar chunk size
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # Menor para mais precisão
    chunk_overlap=100
)

# 2. Aumentar k e filtrar por score
results = vectorstore.similarity_search_with_score(query, k=10)
filtered = [r for r, score in results if score > 0.7]

# 3. Melhorar metadata
# Adicionar mais contexto nos chunks

# 4. Usar modelo de embedding melhor
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
```

### Performance lenta

**Soluções**:
```python
# 1. Criar índice
# Pinecone já tem índice otimizado

# 2. Reduzir k
results = vectorstore.similarity_search(query, k=3)  # Não 10+

# 3. Usar cache
# Ver seção de caching acima

# 4. Implementar busca assíncrona
async def search_async(query):
    return await vectorstore.asimilarity_search(query)
```

## Próximos Passos

- [Engenharia de Prompts](engenharia-prompts.md)
- [Testes](testes-conversacao.md)
- [Otimização de Custos](otimizacao-custos.md)

## Referências

- [LangChain RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)
- [Pinecone Docs](https://docs.pinecone.io/)
- [ChromaDB Docs](https://docs.trychroma.com/)
