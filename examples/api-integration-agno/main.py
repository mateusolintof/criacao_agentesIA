"""
Exemplo: Integração com APIs Externas usando AGNO

Demonstra como criar um agente que interage com APIs externas,
incluindo retry logic, error handling e caching.
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

from api_client import CRMAPIClient

# Carregar variáveis de ambiente
load_dotenv()


class CRMToolkit(Toolkit):
    """Toolkit para integração com CRM API."""
    
    def __init__(self, api_client: CRMAPIClient):
        super().__init__(name="crm_toolkit")
        self.api_client = api_client
        
        # Registrar todas as funções
        self.register(self.search_customer)
        self.register(self.get_customer_details)
        self.register(self.create_customer)
        self.register(self.list_deals)
        self.register(self.create_deal)
    
    def search_customer(self, query: str) -> str:
        """
        Busca clientes por nome, email ou empresa.
        
        Args:
            query: Termo de busca (nome, email ou empresa)
        
        Returns:
            Lista de clientes encontrados
        """
        customers = self.api_client.search_customers(query=query, limit=5)
        
        if not customers:
            return f"Não encontrei clientes com '{query}'"
        
        result = f"Encontrei {len(customers)} cliente(s):\n\n"
        for customer in customers:
            result += f"• {customer.name}\n"
            result += f"  Email: {customer.email}\n"
            if customer.company:
                result += f"  Empresa: {customer.company}\n"
            result += f"  ID: {customer.id}\n\n"
        
        return result
    
    def get_customer_details(self, customer_id: str) -> str:
        """
        Obtém detalhes completos de um cliente.
        
        Args:
            customer_id: ID do cliente
        
        Returns:
            Informações detalhadas do cliente
        """
        customer = self.api_client.get_customer(customer_id)
        
        if not customer:
            return f"Cliente {customer_id} não encontrado"
        
        result = f"📋 Detalhes do Cliente:\n\n"
        result += f"Nome: {customer.name}\n"
        result += f"Email: {customer.email}\n"
        if customer.phone:
            result += f"Telefone: {customer.phone}\n"
        if customer.company:
            result += f"Empresa: {customer.company}\n"
        result += f"Status: {customer.status}\n"
        result += f"ID: {customer.id}\n"
        
        return result
    
    def create_customer(
        self,
        name: str,
        email: str,
        phone: str = None,
        company: str = None
    ) -> str:
        """
        Cria um novo cliente no CRM.
        
        Args:
            name: Nome do cliente
            email: Email do cliente
            phone: Telefone (opcional)
            company: Nome da empresa (opcional)
        
        Returns:
            Confirmação de criação
        """
        customer = self.api_client.create_customer(
            name=name,
            email=email,
            phone=phone,
            company=company
        )
        
        if not customer:
            return "❌ Falha ao criar cliente. Verifique os dados e tente novamente."
        
        result = f"✅ Cliente criado com sucesso!\n\n"
        result += f"Nome: {customer.name}\n"
        result += f"Email: {customer.email}\n"
        result += f"ID: {customer.id}\n"
        
        return result
    
    def list_deals(self, customer_id: str = None, stage: str = None) -> str:
        """
        Lista negociações do CRM.
        
        Args:
            customer_id: Filtrar por cliente específico (opcional)
            stage: Filtrar por estágio (qualification, proposal, negotiation, won, lost)
        
        Returns:
            Lista de negociações
        """
        deals = self.api_client.get_deals(customer_id=customer_id, stage=stage)
        
        if not deals:
            filters = []
            if customer_id:
                filters.append(f"cliente {customer_id}")
            if stage:
                filters.append(f"estágio {stage}")
            filter_str = " com " + " e ".join(filters) if filters else ""
            return f"Não encontrei negociações{filter_str}"
        
        result = f"Encontrei {len(deals)} negociação(ões):\n\n"
        for deal in deals:
            result += f"• {deal.title}\n"
            result += f"  Valor: R$ {deal.value:,.2f}\n"
            result += f"  Estágio: {deal.stage}\n"
            result += f"  Probabilidade: {deal.probability}%\n"
            if deal.expected_close_date:
                result += f"  Fechamento previsto: {deal.expected_close_date}\n"
            result += f"  ID: {deal.id}\n\n"
        
        return result
    
    def create_deal(
        self,
        title: str,
        value: float,
        customer_id: str,
        stage: str = "qualification",
        probability: int = 10
    ) -> str:
        """
        Cria uma nova negociação no CRM.
        
        Args:
            title: Título da negociação
            value: Valor estimado (em reais)
            customer_id: ID do cliente
            stage: Estágio (qualification, proposal, negotiation, won, lost)
            probability: Probabilidade de ganhar 0-100%
        
        Returns:
            Confirmação de criação
        """
        deal = self.api_client.create_deal(
            title=title,
            value=value,
            customer_id=customer_id,
            stage=stage,
            probability=probability
        )
        
        if not deal:
            return "❌ Falha ao criar negociação. Verifique se o cliente existe."
        
        result = f"✅ Negociação criada com sucesso!\n\n"
        result += f"Título: {deal.title}\n"
        result += f"Valor: R$ {deal.value:,.2f}\n"
        result += f"Estágio: {deal.stage}\n"
        result += f"ID: {deal.id}\n"
        
        return result


def create_agent(api_client: CRMAPIClient) -> Agent:
    """Cria o agente AGNO com integração CRM."""
    
    # Configurar database para histórico
    db_file = os.getenv("AGNO_DB_FILE", "./tmp/api_memory.db")
    os.makedirs(os.path.dirname(db_file) if os.path.dirname(db_file) else "./tmp", exist_ok=True)
    
    db = SqliteDb(
        session_table="api_sessions",
        db_file=db_file
    )
    
    # Criar toolkit CRM
    crm_toolkit = CRMToolkit(api_client)
    
    # Instruções do agente
    instructions = [
        "Você é um assistente de vendas com acesso ao CRM da empresa.",
        "",
        "FERRAMENTAS DISPONÍVEIS:",
        "1. search_customer - Buscar clientes por nome, email ou empresa",
        "2. get_customer_details - Ver detalhes completos de um cliente",
        "3. create_customer - Criar novo cliente",
        "4. list_deals - Listar negociações (pode filtrar por cliente ou estágio)",
        "5. create_deal - Criar nova negociação para um cliente",
        "",
        "REGRAS IMPORTANTES:",
        "1. SEMPRE use as ferramentas para acessar dados do CRM",
        "2. Não invente IDs de clientes - sempre busque primeiro",
        "3. Ao criar deals, confirme o ID do cliente antes",
        "4. Seja preciso com valores monetários (use formato R$ X,XXX.XX)",
        "5. Estágios válidos de deal: qualification, proposal, negotiation, won, lost",
        "",
        "ESTILO DE RESPOSTA:",
        "- Seja profissional e direto",
        "- Use formatação clara para listas e dados",
        "- Confirme ações antes de executar (criar, atualizar)",
        "- Se houver erro de API, explique de forma amigável",
        "",
        "SEGURANÇA:",
        "- Nunca compartilhe dados de clientes com terceiros",
        "- Confirme identidade antes de fornecer informações sensíveis",
        "- Não exclua dados sem confirmação explícita"
    ]
    
    # Criar agente AGNO
    agent = Agent(
        name=os.getenv("AGNO_AGENT_NAME", "CRM Assistant"),
        model=OpenAIChat(
            id=os.getenv("OPENAI_MODEL", "gpt-4-turbo"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        ),
        db=db,
        tools=[crm_toolkit],
        add_history_to_context=True,
        num_history_runs=int(os.getenv("AGNO_NUM_HISTORY_RUNS", "5")),
        instructions=instructions,
        markdown=True,
        show_tool_calls=True,
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
    print("🔌  API INTEGRATION - AGNO + CRM")
    print("="*70)
    print("\nAgente com integração a API externa (CRM)")
    print("Demonstra: Retry logic, error handling, caching")
    print("\n⚠️  IMPORTANTE: Inicie o Mock API primeiro:")
    print("   python sample_api.py")
    print("   (ou em outro terminal: uvicorn sample_api:app --port 8001)")
    print("\nDigite 'sair' para encerrar.\n")
    
    # Inicializar API client
    print("Inicializando integração com CRM...")
    api_client = CRMAPIClient()
    
    # Testar conexão
    try:
        import httpx
        response = httpx.get(f"{api_client.base_url}/")
        if response.status_code == 200:
            print("✅ CRM API conectada!\n")
        else:
            print("⚠️  CRM API respondeu mas com erro. Continuando...\n")
    except Exception as e:
        print(f"❌ Não consegui conectar ao CRM API: {e}")
        print("Certifique-se que sample_api.py está rodando na porta 8001")
        print("Continuando mesmo assim (algumas funções podem falhar)...\n")
    
    # Criar agente
    agent = create_agent(api_client)
    print("✅ Agente pronto!\n")
    
    # Gerar session_id único
    import time
    session_id = f"crm_session_{int(time.time())}"
    
    # Loop de conversação
    while True:
        try:
            # Input do usuário
            user_input = input("👤 Você: ").strip()
            
            # Verificar comandos
            if user_input.lower() in ["sair", "quit", "exit", "q"]:
                print("\n👋 Encerrando. Até logo!")
                break
            
            if not user_input:
                continue
            
            # Processar com agente
            print("\n🤖 Assistente: ", end="", flush=True)
            
            # Usar streaming
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
