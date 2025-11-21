"""
Ferramentas (Tools) Customizadas para os Agentes

Tools permitem que agentes executem ações específicas:
- Buscar informações em bases de dados
- Fazer cálculos
- Consultar APIs externas
- Validar dados

No CrewAI, tools são funções decoradas com @tool
"""

from crewai_tools import tool
from typing import Dict, List, Any
from datetime import datetime


# ==================== Sales Tools ====================

@tool("Calcular Desconto")
def calculate_discount(original_price: float, discount_percent: float) -> str:
    """
    Calcula preço com desconto para propostas de vendas.

    Args:
        original_price: Preço original em reais
        discount_percent: Percentual de desconto (0-100)

    Returns:
        Texto formatado com cálculo de desconto
    """
    if discount_percent < 0 or discount_percent > 100:
        return "Erro: Desconto deve estar entre 0% e 100%"

    if discount_percent > 30:
        return f"Erro: Desconto máximo permitido é 30%. Solicitado: {discount_percent}%"

    discount_amount = original_price * (discount_percent / 100)
    final_price = original_price - discount_amount

    return f"""Cálculo de Desconto:
    - Preço Original: R$ {original_price:.2f}
    - Desconto ({discount_percent}%): R$ {discount_amount:.2f}
    - Preço Final: R$ {final_price:.2f}
    - Economia: R$ {discount_amount:.2f}"""


@tool("Verificar Disponibilidade de Demo")
def check_demo_availability(preferred_date: str = None) -> str:
    """
    Verifica disponibilidade para agendar demonstração.

    Args:
        preferred_date: Data preferida no formato YYYY-MM-DD (opcional)

    Returns:
        Texto com horários disponíveis
    """
    # Simulação - em produção consultaria calendário real
    return f"""Horários disponíveis para demonstração:

    Esta semana:
    - Terça-feira (14h, 16h)
    - Quarta-feira (10h, 14h, 16h)
    - Quinta-feira (14h)

    Próxima semana:
    - Segunda a sexta (10h, 14h, 16h)

    Duração: 30-45 minutos
    Formato: Online via Google Meet

    Para agendar, informe o dia e horário preferidos."""


@tool("Buscar Informações de Cliente")
def get_customer_info(email: str) -> str:
    """
    Busca informações de cliente existente no CRM.

    Args:
        email: Email do cliente

    Returns:
        Informações do cliente ou mensagem de não encontrado
    """
    # Simulação - em produção consultaria CRM real
    mock_customers = {
        "joao@empresa.com": {
            "nome": "João Silva",
            "empresa": "TechCorp",
            "plano_atual": "CRM Enterprise",
            "status": "Cliente ativo desde 2024-01"
        },
        "maria@startup.com": {
            "nome": "Maria Santos",
            "empresa": "Startup XYZ",
            "plano_atual": "Trial - AI Assistant",
            "status": "Trial expira em 5 dias"
        }
    }

    if email in mock_customers:
        customer = mock_customers[email]
        return f"""Informações do Cliente:
        - Nome: {customer['nome']}
        - Empresa: {customer['empresa']}
        - Plano: {customer['plano_atual']}
        - Status: {customer['status']}"""
    else:
        return f"Cliente não encontrado no sistema para o email: {email}"


# ==================== Support Tools ====================

@tool("Consultar Status do Sistema")
def check_system_status() -> str:
    """
    Verifica status dos sistemas e serviços.

    Returns:
        Status atual de todos os serviços
    """
    # Simulação - em produção consultaria monitoring real
    return """Status dos Sistemas (atualizado em tempo real):

    ✓ CRM Enterprise: Operacional (99.9% uptime)
    ✓ AI Assistant API: Operacional
    ✓ Analytics Suite: Operacional
    ✓ Autenticação (SSO): Operacional
    ⚠ Webhooks: Latência elevada (~500ms, normal <200ms)

    Nenhum incidente ativo.
    Próxima manutenção programada: Domingo 03:00-05:00 AM"""


@tool("Buscar Documentação")
def search_documentation(query: str) -> str:
    """
    Busca na documentação técnica.

    Args:
        query: Termo de busca

    Returns:
        Links e resumos de documentação relevante
    """
    # Simulação - em produção faria busca real na doc
    docs = {
        "api": """Documentação API REST:
        - Autenticação: https://docs.empresa.com/api/auth
        - Endpoints: https://docs.empresa.com/api/endpoints
        - Rate Limits: 1000 requests/hora
        - Exemplos: https://docs.empresa.com/api/examples""",

        "integração": """Guias de Integração:
        - Salesforce: https://docs.empresa.com/integrations/salesforce
        - HubSpot: https://docs.empresa.com/integrations/hubspot
        - Webhooks: https://docs.empresa.com/integrations/webhooks
        - Zapier: https://docs.empresa.com/integrations/zapier""",

        "configuração": """Configuração Inicial:
        - Setup Rápido: https://docs.empresa.com/quickstart
        - Configuração Avançada: https://docs.empresa.com/advanced-config
        - Melhores Práticas: https://docs.empresa.com/best-practices"""
    }

    query_lower = query.lower()
    for key, doc in docs.items():
        if key in query_lower:
            return doc

    return f"""Resultados para "{query}":
    - Central de Ajuda: https://docs.empresa.com/search?q={query}
    - Vídeos Tutoriais: https://youtube.com/empresa
    - Comunidade: https://community.empresa.com"""


@tool("Verificar Logs de Erro")
def check_error_logs(customer_id: str, last_hours: int = 24) -> str:
    """
    Verifica logs de erro para diagnóstico.

    Args:
        customer_id: ID do cliente
        last_hours: Últimas N horas de logs (padrão: 24)

    Returns:
        Resumo de erros encontrados
    """
    # Simulação - em produção consultaria logs reais
    return f"""Logs de Erro - Cliente {customer_id} (últimas {last_hours}h):

    Erros encontrados: 3

    1. [2024-11-20 14:23] API Rate Limit
       - Endpoint: /api/v1/contacts
       - Status: 429
       - Ação: Cliente excedeu limite de 1000 req/h

    2. [2024-11-20 10:15] Authentication Failed
       - Tentativas: 2
       - Motivo: Token expirado
       - Ação: Token renovado automaticamente

    3. [2024-11-19 18:45] Webhook Timeout
       - URL: https://cliente.com/webhook
       - Timeout após 30s
       - Ação: Retry bem-sucedido

    Recomendação: Revisar rate limits e timeout do webhook."""


# ==================== Product Tools ====================

@tool("Comparar Planos")
def compare_plans(plan_a: str, plan_b: str) -> str:
    """
    Compara dois planos de produtos.

    Args:
        plan_a: Nome do primeiro plano
        plan_b: Nome do segundo plano

    Returns:
        Comparação detalhada
    """
    plans = {
        "crm": {
            "nome": "CRM Enterprise",
            "preco": 199,
            "usuarios": "Até 10 usuários",
            "features": ["Pipeline de vendas", "Automação", "Relatórios básicos"],
            "suporte": "Email e chat"
        },
        "ai": {
            "nome": "AI Assistant",
            "preco": 499,
            "usuarios": "Até 20 usuários",
            "features": ["Chatbots IA", "Automação avançada", "Fine-tuning", "API"],
            "suporte": "Email, chat e dedicado"
        },
        "analytics": {
            "nome": "Analytics Suite",
            "preco": 299,
            "usuarios": "Até 15 usuários",
            "features": ["Dashboards", "50+ conectores", "SQL queries", "Alertas"],
            "suporte": "Email e chat"
        }
    }

    plan_a_key = plan_a.lower().replace(" ", "")
    plan_b_key = plan_b.lower().replace(" ", "")

    # Mapeamento flexível
    if "crm" in plan_a_key: plan_a_key = "crm"
    elif "ai" in plan_a_key or "assistant" in plan_a_key: plan_a_key = "ai"
    elif "analytics" in plan_a_key: plan_a_key = "analytics"

    if "crm" in plan_b_key: plan_b_key = "crm"
    elif "ai" in plan_b_key or "assistant" in plan_b_key: plan_b_key = "ai"
    elif "analytics" in plan_b_key: plan_b_key = "analytics"

    if plan_a_key not in plans or plan_b_key not in plans:
        return "Erro: Plano não encontrado. Planos disponíveis: CRM, AI, Analytics"

    a = plans[plan_a_key]
    b = plans[plan_b_key]

    return f"""Comparação de Planos:

    {a['nome']} vs {b['nome']}

    Preço:
    - {a['nome']}: R$ {a['preco']}/mês
    - {b['nome']}: R$ {b['preco']}/mês
    - Diferença: R$ {abs(a['preco'] - b['preco'])}/mês

    Usuários:
    - {a['nome']}: {a['usuarios']}
    - {b['nome']}: {b['usuarios']}

    Features principais:
    - {a['nome']}: {', '.join(a['features'])}
    - {b['nome']}: {', '.join(b['features'])}

    Suporte:
    - {a['nome']}: {a['suporte']}
    - {b['nome']}: {b['suporte']}"""


@tool("Obter Roadmap")
def get_product_roadmap(product: str) -> str:
    """
    Obtém roadmap de features futuras.

    Args:
        product: Nome do produto

    Returns:
        Roadmap com próximas features
    """
    roadmaps = {
        "crm": """Roadmap CRM Enterprise (Q1-Q2 2025):

        Em Desenvolvimento:
        - ✓ Integração com WhatsApp Business (Jan 2025)
        - ✓ Mobile app iOS/Android (Fev 2025)

        Planejado:
        - Pipeline visual Kanban (Mar 2025)
        - Automação com IA (Abr 2025)
        - Integrações: Slack, Teams (Mai 2025)""",

        "ai": """Roadmap AI Assistant (Q1-Q2 2025):

        Em Desenvolvimento:
        - ✓ Suporte a GPT-4o e Claude 3.5 (Jan 2025)
        - ✓ Voice assistants (Fev 2025)

        Planejado:
        - Multi-modal (imagens, vídeos) (Mar 2025)
        - Agents autônomos (Abr 2025)
        - Fine-tuning simplificado (Mai 2025)""",

        "analytics": """Roadmap Analytics Suite (Q1-Q2 2025):

        Em Desenvolvimento:
        - ✓ Real-time dashboards (Jan 2025)
        - ✓ AI-powered insights (Fev 2025)

        Planejado:
        - Natural language queries (Mar 2025)
        - Predictive analytics (Abr 2025)
        - Embedded analytics (Mai 2025)"""
    }

    product_key = product.lower()
    if "crm" in product_key:
        return roadmaps["crm"]
    elif "ai" in product_key or "assistant" in product_key:
        return roadmaps["ai"]
    elif "analytics" in product_key:
        return roadmaps["analytics"]
    else:
        return "Produto não encontrado. Disponíveis: CRM, AI Assistant, Analytics"


# ==================== Factory Functions ====================

def create_sales_tools() -> List:
    """Retorna lista de ferramentas para o agente de vendas."""
    return [
        calculate_discount,
        check_demo_availability,
        get_customer_info,
        compare_plans
    ]


def create_support_tools() -> List:
    """Retorna lista de ferramentas para o agente de suporte."""
    return [
        check_system_status,
        search_documentation,
        check_error_logs
    ]


def create_product_tools() -> List:
    """Retorna lista de ferramentas para o agente de produto."""
    return [
        compare_plans,
        get_product_roadmap
    ]
