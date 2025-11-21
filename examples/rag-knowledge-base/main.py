"""
Exemplo: RAG Knowledge Base com AGNO

Sistema de Q&A sobre base de conhecimento usando Retrieval-Augmented Generation.
Framework: AGNO
Atualizado: 2025-11-20
"""

import os
import sys
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb
from agno.tools.toolkit import Toolkit

from vector_store import VectorStore
from knowledge_loader import KnowledgeLoader

# Carregar variáveis de ambiente
load_dotenv()


class KnowledgeToolkit(Toolkit):
    """Toolkit para busca na base de conhecimento."""
    
    def __init__(self, vector_store: VectorStore, top_k: int = 3):
        super().__init__(name="knowledge_toolkit")
        self.vector_store = vector_store
        self.top_k = top_k
        
        # Registrar funções
        self.register(self.search_knowledge)
    
    def search_knowledge(self, query: str) -> str:
        """
        Busca informações relevantes na base de conhecimento.
        
        Args:
            query: Pergunta ou termo de busca
        
        Returns:
            Documentos relevantes encontrados
        """
        results = self.vector_store.search(query, top_k=self.top_k)
        
        if not results:
            return "Não encontrei informações relevantes sobre isso na base de conhecimento."
        
        # Formatar resultados
        formatted = "📚 Informações encontradas na base de conhecimento:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"--- Documento {i} ---\n"
            formatted += f"Fonte: {result['metadata'].get('filename', 'unknown')}\n"
            formatted += f"Conteúdo:\n{result['document']}\n\n"
        
        return formatted


def initialize_knowledge_base() -> VectorStore:
    """Inicializa e carrega a base de conhecimento."""
    
    # Configurar vector store
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./tmp/chroma_db")
    embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    vector_store = VectorStore(
        persist_dir=persist_dir,
        collection_name="knowledge_base",
        embedding_model=embedding_model
    )
    
    # Verificar se já tem documentos
    if vector_store.count() > 0:
        print(f"✅ Base de conhecimento já carregada ({vector_store.count()} chunks)")
        return vector_store
    
    print("📚 Carregando base de conhecimento...")
    
    # Configurar loader
    chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
    loader = KnowledgeLoader(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    # Carregar documentos da pasta sample_docs
    docs_dir = os.path.join(os.path.dirname(__file__), "sample_docs")
    if not os.path.exists(docs_dir):
        print(f"⚠️  Diretório {docs_dir} não encontrado. Criando vazio...")
        os.makedirs(docs_dir, exist_ok=True)
        return vector_store
    
    # Carregar e processar documentos
    documents = loader.load_directory(docs_dir)
    
    if not documents:
        print("⚠️  Nenhum documento encontrado em sample_docs/")
        return vector_store
    
    # Adicionar ao vector store
    texts = [doc['text'] for doc in documents]
    metadatas = [doc['metadata'] for doc in documents]
    ids = [f"{doc['metadata']['filename']}_{doc['metadata']['chunk']}" for doc in documents]
    
    vector_store.add_documents(texts, metadatas, ids)
    
    print(f"✅ {len(documents)} chunks adicionados à base de conhecimento")
    
    return vector_store


def create_agent(vector_store: VectorStore) -> Agent:
    """Cria o agente AGNO com RAG."""
    
    # Configurar database para histórico
    db_file = os.getenv("AGNO_DB_FILE", "./tmp/rag_memory.db")
    os.makedirs(os.path.dirname(db_file) if os.path.dirname(db_file) else "./tmp", exist_ok=True)
    
    db = SqliteDb(
        session_table="rag_sessions",
        db_file=db_file
    )
    
    # Criar toolkit de conhecimento
    top_k = int(os.getenv("TOP_K_RESULTS", "3"))
    knowledge_toolkit = KnowledgeToolkit(vector_store, top_k=top_k)
    
    # Instruções do agente (lista de strings - padrão AGNO)
    instructions = [
        "Você é um assistente especializado em responder perguntas sobre nossa base de conhecimento.",
        "",
        "REGRAS IMPORTANTES:",
        "1. SEMPRE use a função 'search_knowledge' para buscar informações antes de responder",
        "2. Base suas respostas APENAS nas informações encontradas na base de conhecimento",
        "3. Se não encontrar informações relevantes, seja honesto e diga que não sabe",
        "4. NUNCA invente ou alucinne informações que não estão na base",
        "5. Cite a fonte quando possível (nome do documento)",
        "6. Se a pergunta for ambígua, peça esclarecimentos",
        "",
        "ESTILO DE RESPOSTA:",
        "- Seja claro, direto e profissional",
        "- Use formatação markdown quando apropriado",
        "- Para informações técnicas, seja preciso",
        "- Para preços e datas, sempre cite a fonte e data de atualização",
        "",
        "LIMITAÇÕES:",
        "- Você só tem acesso à base de conhecimento carregada",
        "- Não tem informações em tempo real",
        "- Para questões fora da base, direcione ao contato apropriado"
    ]
    
    # Criar agente AGNO
    agent = Agent(
        name=os.getenv("AGNO_AGENT_NAME", "Knowledge Assistant"),
        model=OpenAIChat(
            id=os.getenv("OPENAI_MODEL", "gpt-4-turbo"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        ),
        db=db,
        tools=[knowledge_toolkit],
        add_history_to_context=True,
        num_history_runs=int(os.getenv("AGNO_NUM_HISTORY_RUNS", "3")),
        instructions=instructions,
        markdown=True,
        show_tool_calls=True,  # Mostrar quando usa a busca
    )
    
    return agent


def main():
    """Função principal."""
    
    # Verificar API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Erro: OPENAI_API_KEY não configurada.")
        print("Configure no arquivo .env")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("📚  RAG KNOWLEDGE BASE - AGNO")
    print("="*70)
    print("\nSistema de perguntas e respostas sobre base de conhecimento")
    print("usando Retrieval-Augmented Generation (RAG)")
    print("\nDigite 'sair' para encerrar, 'limpar' para nova sessão.\n")
    
    # Inicializar base de conhecimento
    print("Inicializando sistema...")
    vector_store = initialize_knowledge_base()
    
    # Criar agente
    agent = create_agent(vector_store)
    print("✅ Sistema pronto!\n")
    
    # Gerar session_id único
    import time
    session_id = f"rag_session_{int(time.time())}"
    
    # Loop de conversação
    while True:
        try:
            # Input do usuário
            user_input = input("👤 Você: ").strip()
            
            # Verificar comandos
            if user_input.lower() in ["sair", "quit", "exit", "q"]:
                print("\n👋 Encerrando. Até logo!")
                break
            
            if user_input.lower() == "limpar":
                session_id = f"rag_session_{int(time.time())}"
                print("🔄 Nova sessão iniciada!\n")
                continue
            
            if not user_input:
                continue
            
            # Processar com agente
            print("\n🤖 Assistente: ", end="", flush=True)
            
            # Usar streaming para resposta em tempo real
            response = agent.run(
                user_input,
                session_id=session_id,
                stream=True
            )
            
            # Stream de resposta
            for chunk in response:
                print(chunk, end="", flush=True)
            
            print("\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrompido. Até logo!")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            print("Continuando...\n")


if __name__ == "__main__":
    main()
