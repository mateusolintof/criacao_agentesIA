"""
Vector Store com ChromaDB para RAG
Atualizado: 2025-11-20
"""

import os
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


class VectorStore:
    """Gerencia embeddings e busca vetorial com ChromaDB."""
    
    def __init__(
        self,
        persist_dir: str = "./tmp/chroma_db",
        collection_name: str = "knowledge_base",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Inicializa o vector store.
        
        Args:
            persist_dir: Diretório para persistir embeddings
            collection_name: Nome da coleção no ChromaDB
            embedding_model: Modelo de embeddings do sentence-transformers
        """
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        
        # Criar diretório se não existir
        os.makedirs(persist_dir, exist_ok=True)
        
        # Inicializar ChromaDB
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # Inicializar modelo de embeddings
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Obter ou criar coleção
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Knowledge base for RAG"}
        )
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]] = None,
        ids: List[str] = None
    ) -> None:
        """
        Adiciona documentos ao vector store.
        
        Args:
            documents: Lista de textos a adicionar
            metadatas: Metadados opcionais para cada documento
            ids: IDs opcionais para cada documento
        """
        if not documents:
            return
        
        # Gerar embeddings
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # Gerar IDs se não fornecidos
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        
        # Adicionar à coleção
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(
        self,
        query: str,
        top_k: int = 3,
        where: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca documentos relevantes.
        
        Args:
            query: Texto da busca
            top_k: Quantos resultados retornar
            where: Filtros opcionais de metadata
        
        Returns:
            Lista de dicionários com 'document', 'metadata' e 'distance'
        """
        # Gerar embedding da query
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Buscar na coleção
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            where=where
        )
        
        # Formatar resultados
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                'distance': results['distances'][0][i]
            })
        
        return formatted_results
    
    def clear(self) -> None:
        """Remove todos os documentos da coleção."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Knowledge base for RAG"}
        )
    
    def count(self) -> int:
        """Retorna o número de documentos na coleção."""
        return self.collection.count()
