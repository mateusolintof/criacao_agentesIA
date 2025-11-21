"""
Knowledge Loader - Processa e carrega documentos para RAG
Atualizado: 2025-11-20
"""

import os
from typing import List, Dict, Any
from pathlib import Path
import markdown
from pypdf import PdfReader
from bs4 import BeautifulSoup


class KnowledgeLoader:
    """Carrega e processa documentos de várias fontes."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Inicializa o loader.
        
        Args:
            chunk_size: Tamanho máximo de cada chunk
            chunk_overlap: Overlap entre chunks consecutivos
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def load_directory(
        self,
        directory: str,
        extensions: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Carrega todos os documentos de um diretório.
        
        Args:
            directory: Caminho do diretório
            extensions: Extensões de arquivo a processar (None = todas)
        
        Returns:
            Lista de dicionários com 'text' e 'metadata'
        """
        if extensions is None:
            extensions = ['.txt', '.md', '.pdf', '.html']
        
        documents = []
        directory_path = Path(directory)
        
        for file_path in directory_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in extensions:
                try:
                    doc = self.load_file(str(file_path))
                    documents.extend(doc)
                except Exception as e:
                    print(f"⚠️  Erro ao carregar {file_path}: {e}")
        
        return documents
    
    def load_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Carrega um arquivo específico.
        
        Args:
            file_path: Caminho do arquivo
        
        Returns:
            Lista de dicionários com 'text' e 'metadata'
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        # Carregar conteúdo baseado na extensão
        if extension == '.txt':
            content = self._load_txt(file_path)
        elif extension == '.md':
            content = self._load_markdown(file_path)
        elif extension == '.pdf':
            content = self._load_pdf(file_path)
        elif extension == '.html':
            content = self._load_html(file_path)
        else:
            raise ValueError(f"Tipo de arquivo não suportado: {extension}")
        
        # Dividir em chunks
        chunks = self._split_text(content)
        
        # Criar documentos com metadata
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append({
                'text': chunk,
                'metadata': {
                    'source': str(file_path),
                    'filename': file_path.name,
                    'chunk': i,
                    'total_chunks': len(chunks)
                }
            })
        
        return documents
    
    def _load_txt(self, file_path: Path) -> str:
        """Carrega arquivo .txt"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _load_markdown(self, file_path: Path) -> str:
        """Carrega arquivo .md e converte para texto"""
        with open(file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        # Converter markdown para HTML e depois para texto
        html = markdown.markdown(md_content)
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text()
    
    def _load_pdf(self, file_path: Path) -> str:
        """Carrega arquivo .pdf"""
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    
    def _load_html(self, file_path: Path) -> str:
        """Carrega arquivo .html"""
        with open(file_path, 'r', encoding='utf-8') as f:
            html = f.read()
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text()
    
    def _split_text(self, text: str) -> List[str]:
        """
        Divide texto em chunks com overlap.
        
        Args:
            text: Texto a dividir
        
        Returns:
            Lista de chunks
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Definir fim do chunk
            end = start + self.chunk_size
            
            # Se não é o último chunk, tentar quebrar em espaço
            if end < len(text):
                # Procurar último espaço antes do fim
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
            
            # Adicionar chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Mover para próximo chunk com overlap
            start = end - self.chunk_overlap
            if start <= 0 or start >= len(text):
                break
        
        return chunks
