"""
Template: Sales Agent com AGNO Framework

Agente especializado em vendas e qualificação de leads usando AGNO.
Este é um exemplo completo e pronto para produção de um Sales Agent.

Funcionalidades:
- Qualificação de leads (BANT)
- Apresentação de produtos do catálogo
- Integração com CRM
- Agendamento de demos
- Tratamento de objeções
- Memória persistente de conversas
"""

from typing import Dict, List, Any, Optional
import json
from datetime import datetime
import logging

# AGNO Framework imports
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb
from agno.tools.toolkit import Toolkit


# ==================== Sales Toolkit ====================

class SalesToolkit(Toolkit):
    """
    Toolkit de vendas com ferramentas para:
    - Buscar produtos no catálogo
    - Consultar detalhes de produtos
    - Criar leads no CRM
    - Agendar demonstrações
    - Calcular descontos
    """

    def __init__(
        self,
        product_catalog: Optional[List[Dict[str, Any]]] = None,
        crm_client: Optional[Any] = None
    ):
        """
        Inicializa Sales Toolkit.

        Args:
            product_catalog: Catálogo de produtos (opcional)
            crm_client: Cliente CRM para integração (opcional)
        """
        super().__init__(name="sales_toolkit")
        self.product_catalog = product_catalog or self._load_default_catalog()
        self.crm_client = crm_client
        self.logger = logging.getLogger("SalesToolkit")

    def search_products(
        self,
        query: str,
        category: Optional[str] = None,
        max_results: int = 5
    ) -> str:
        """
        Busca produtos no catálogo por nome, descrição ou funcionalidades.

        Args:
            query: Termo de busca
            category: Filtrar por categoria (opcional)
            max_results: Número máximo de resultados (default: 5)

        Returns:
            JSON string com produtos encontrados
        """
        try:
            results = []
            query_lower = query.lower()

            for product in self.product_catalog:
                # Busca em nome, descrição e features
                matches = (
                    query_lower in product["name"].lower() or
                    query_lower in product["description"].lower() or
                    any(query_lower in feat.lower() for feat in product["features"])
                )

                if matches:
                    # Filtrar por categoria se especificada
                    if category and product["category"].lower() != category.lower():
                        continue

                    results.append({
                        "id": product["id"],
                        "name": product["name"],
                        "category": product["category"],
                        "description": product["description"],
                        "starting_price": product["pricing"]["starting_at"],
                        "currency": product["pricing"]["currency"]
                    })

            return json.dumps({
                "success": True,
                "results": results[:max_results],
                "total_found": len(results)
            }, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error searching products: {e}")
            return json.dumps({"success": False, "error": str(e)})

    def get_product_details(self, product_id: str) -> str:
        """
        Obtém detalhes completos de um produto específico.

        Args:
            product_id: ID do produto (ex: "prod-001")

        Returns:
            JSON string com detalhes completos do produto
        """
        try:
            product = next(
                (p for p in self.product_catalog if p["id"] == product_id),
                None
            )

            if not product:
                return json.dumps({
                    "success": False,
                    "error": f"Produto {product_id} não encontrado"
                })

            return json.dumps({
                "success": True,
                "product": product
            }, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error getting product details: {e}")
            return json.dumps({"success": False, "error": str(e)})

    def check_product_availability(
        self,
        product_id: str,
        region: str = "BR"
    ) -> str:
        """
        Verifica disponibilidade e prazo de entrega de um produto.

        Args:
            product_id: ID do produto
            region: Região para consulta (default: "BR")

        Returns:
            JSON string com informações de disponibilidade
        """
        try:
            # Simulação - em produção, consultaria API real
            product = next(
                (p for p in self.product_catalog if p["id"] == product_id),
                None
            )

            if not product:
                return json.dumps({
                    "success": False,
                    "error": "Produto não encontrado"
                })

            return json.dumps({
                "success": True,
                "product_id": product_id,
                "product_name": product["name"],
                "available": True,
                "delivery_time": "Imediato (SaaS)",
                "region": region,
                "setup_time": "3-5 dias úteis",
                "message": "Produto disponível para ativação imediata"
            }, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error checking availability: {e}")
            return json.dumps({"success": False, "error": str(e)})

    def create_lead(
        self,
        name: str,
        email: str,
        company: Optional[str] = None,
        phone: Optional[str] = None,
        interest: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """
        Cria um novo lead no CRM.

        Args:
            name: Nome completo do lead
            email: Email de contato
            company: Empresa (opcional)
            phone: Telefone (opcional)
            interest: Produtos/serviços de interesse (opcional)
            notes: Observações adicionais (opcional)

        Returns:
            JSON string com resultado da criação
        """
        try:
            lead_data = {
                "name": name,
                "email": email,
                "company": company,
                "phone": phone,
                "interest": interest,
                "notes": notes,
                "source": "sales_agent_ai",
                "status": "new",
                "created_at": datetime.utcnow().isoformat()
            }

            # Se tem integração CRM real, usar
            if self.crm_client:
                result = self.crm_client.create_lead(lead_data)
                lead_id = result.get("id")
            else:
                # Simulação
                lead_id = f"LEAD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
                self.logger.info(f"Lead created (simulated): {lead_id} - {email}")

            return json.dumps({
                "success": True,
                "lead_id": lead_id,
                "message": f"Lead {name} criado com sucesso no CRM",
                "next_steps": "Aguardar contato do time comercial em até 24h"
            }, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error creating lead: {e}")
            return json.dumps({"success": False, "error": str(e)})

    def schedule_demo(
        self,
        lead_email: str,
        product_id: str,
        preferred_date: str,
        preferred_time: Optional[str] = None
    ) -> str:
        """
        Agenda uma demonstração do produto para o lead.

        Args:
            lead_email: Email do lead
            product_id: ID do produto para demonstração
            preferred_date: Data preferida (formato: YYYY-MM-DD)
            preferred_time: Horário preferido (opcional, ex: "14:00")

        Returns:
            JSON string com confirmação do agendamento
        """
        try:
            product = next(
                (p for p in self.product_catalog if p["id"] == product_id),
                None
            )

            if not product:
                return json.dumps({
                    "success": False,
                    "error": "Produto não encontrado"
                })

            demo_id = f"DEMO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

            # Simulação - em produção, integraria com calendário (Calendly, etc)
            self.logger.info(
                f"Demo scheduled: {demo_id} - {lead_email} - "
                f"{product['name']} - {preferred_date}"
            )

            time_info = f" às {preferred_time}" if preferred_time else ""

            return json.dumps({
                "success": True,
                "demo_id": demo_id,
                "product": product["name"],
                "date": preferred_date,
                "time": preferred_time or "A confirmar",
                "message": (
                    f"Demonstração de {product['name']} agendada para "
                    f"{preferred_date}{time_info}. "
                    f"Você receberá confirmação por email em {lead_email}."
                )
            }, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error scheduling demo: {e}")
            return json.dumps({"success": False, "error": str(e)})

    def calculate_pricing(
        self,
        product_id: str,
        num_users: int,
        billing_period: str = "monthly",
        discount_code: Optional[str] = None
    ) -> str:
        """
        Calcula preço personalizado baseado em número de usuários e período.

        Args:
            product_id: ID do produto
            num_users: Número de usuários
            billing_period: Período de cobrança ("monthly" ou "yearly")
            discount_code: Código de desconto (opcional)

        Returns:
            JSON string com cálculo de preço
        """
        try:
            product = next(
                (p for p in self.product_catalog if p["id"] == product_id),
                None
            )

            if not product:
                return json.dumps({
                    "success": False,
                    "error": "Produto não encontrado"
                })

            base_price = product["pricing"]["starting_at"]

            # Calcular preço por usuário (simplificado)
            if num_users <= 10:
                price_per_user = base_price
            elif num_users <= 50:
                price_per_user = base_price * 0.9  # 10% desconto
            else:
                price_per_user = base_price * 0.8  # 20% desconto

            monthly_total = price_per_user * num_users

            # Desconto para pagamento anual
            if billing_period == "yearly":
                yearly_total = monthly_total * 12 * 0.85  # 15% desconto
                monthly_equivalent = yearly_total / 12
            else:
                yearly_total = monthly_total * 12
                monthly_equivalent = monthly_total

            # Aplicar código de desconto (exemplo)
            discount_percent = 0
            if discount_code:
                # Simplificado - em produção, validaria códigos reais
                if discount_code.upper() == "PROMO10":
                    discount_percent = 10
                elif discount_code.upper() == "PROMO20":
                    discount_percent = 20

            if discount_percent > 0:
                discount_amount = monthly_equivalent * (discount_percent / 100)
                final_monthly = monthly_equivalent - discount_amount
            else:
                discount_amount = 0
                final_monthly = monthly_equivalent

            return json.dumps({
                "success": True,
                "product": product["name"],
                "num_users": num_users,
                "billing_period": billing_period,
                "base_price_per_user": base_price,
                "price_per_user": price_per_user,
                "monthly_total": round(monthly_total, 2),
                "discount_code": discount_code,
                "discount_percent": discount_percent,
                "discount_amount": round(discount_amount, 2),
                "final_monthly_price": round(final_monthly, 2),
                "yearly_total": round(yearly_total, 2) if billing_period == "yearly" else round(final_monthly * 12, 2),
                "currency": "BRL",
                "savings": round(
                    (monthly_total * 12) - yearly_total if billing_period == "yearly" else discount_amount,
                    2
                )
            }, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error calculating pricing: {e}")
            return json.dumps({"success": False, "error": str(e)})

    def _load_default_catalog(self) -> List[Dict[str, Any]]:
        """Carrega catálogo de produtos padrão."""
        return [
            {
                "id": "prod-001",
                "name": "Enterprise CRM Pro",
                "category": "CRM",
                "description": "Solução completa de CRM para gestão de vendas e relacionamento com clientes empresariais",
                "features": [
                    "Gestão completa de pipeline de vendas",
                    "Automação de marketing e email campaigns",
                    "Relatórios e analytics avançados",
                    "Integração com WhatsApp, email e telefonia",
                    "Mobile app iOS e Android",
                    "API REST para integrações",
                    "Suporte prioritário 24/7"
                ],
                "pricing": {
                    "model": "per_user_subscription",
                    "starting_at": 199.00,
                    "currency": "BRL",
                    "billing": "monthly"
                },
                "target_audience": "Empresas de 50-500 funcionários",
                "benefits": [
                    "Aumento de 35% em conversão de leads",
                    "Redução de 50% em tempo de follow-up",
                    "Visibilidade completa do funil de vendas"
                ]
            },
            {
                "id": "prod-002",
                "name": "AI Sales Assistant",
                "category": "AI",
                "description": "Assistente de vendas com Inteligência Artificial para qualificação automática de leads 24/7",
                "features": [
                    "Qualificação automática de leads (BANT)",
                    "Atendimento 24/7 em múltiplos canais",
                    "Análise de sentimento e intenção",
                    "Integração nativa com CRMs principais",
                    "Multi-idioma (PT, EN, ES)",
                    "Relatórios de performance e insights",
                    "Treinamento contínuo com seus dados"
                ],
                "pricing": {
                    "model": "subscription",
                    "starting_at": 499.00,
                    "currency": "BRL",
                    "billing": "monthly"
                },
                "target_audience": "Empresas com alto volume de leads (100+ por mês)",
                "benefits": [
                    "Qualificação 3x mais rápida de leads",
                    "Economia de 60% em custo de SDRs",
                    "Taxa de resposta de 98% em menos de 1 minuto"
                ]
            },
            {
                "id": "prod-003",
                "name": "Sales Analytics Suite",
                "category": "Analytics",
                "description": "Plataforma de Business Intelligence e Analytics especializada em vendas B2B",
                "features": [
                    "Dashboards interativos e personalizáveis",
                    "Forecasting de vendas com IA",
                    "Análise de conversão por etapa do funil",
                    "Alertas inteligentes e anomalias",
                    "Benchmarking com mercado",
                    "Exportação de relatórios (PDF, Excel)",
                    "Integração com CRMs e ERPs"
                ],
                "pricing": {
                    "model": "subscription",
                    "starting_at": 299.00,
                    "currency": "BRL",
                    "billing": "monthly"
                },
                "target_audience": "Gestores e diretores comerciais",
                "benefits": [
                    "Previsibilidade 40% maior de receita",
                    "Identificação antecipada de riscos",
                    "Decisões baseadas em dados confiáveis"
                ]
            },
            {
                "id": "prod-004",
                "name": "Sales Enablement Platform",
                "category": "Enablement",
                "description": "Plataforma completa para capacitação, treinamento e produtividade de times de vendas",
                "features": [
                    "Biblioteca de conteúdos de vendas",
                    "Treinamentos e certificações",
                    "Playbooks e scripts de vendas",
                    "Role-playing com IA",
                    "Acompanhamento de performance individual",
                    "Gamificação e ranking",
                    "Onboarding automatizado"
                ],
                "pricing": {
                    "model": "per_user_subscription",
                    "starting_at": 149.00,
                    "currency": "BRL",
                    "billing": "monthly"
                },
                "target_audience": "Times de vendas de 10+ pessoas",
                "benefits": [
                    "Redução de 50% em tempo de onboarding",
                    "Aumento de 25% em performance de vendedores",
                    "Padronização de processos comerciais"
                ]
            }
        ]


# ==================== Sales Agent ====================

class SalesAgent:
    """
    Agente de vendas completo usando AGNO Framework.

    Funcionalidades:
    - Atendimento comercial consultivo
    - Qualificação de leads (BANT)
    - Apresentação de produtos
    - Tratamento de objeções
    - Agendamento de demos
    - Integração com CRM
    - Memória de conversas
    """

    def __init__(
        self,
        model_id: str = "gpt-4",
        db_path: str = "/tmp/sales_agent.db",
        product_catalog: Optional[List[Dict[str, Any]]] = None,
        crm_client: Optional[Any] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Inicializa Sales Agent.

        Args:
            model_id: ID do modelo LLM (default: gpt-4)
            db_path: Caminho para banco SQLite de memória
            product_catalog: Catálogo de produtos customizado (opcional)
            crm_client: Cliente CRM para integração (opcional)
            logger: Logger customizado (opcional)
        """
        self.logger = logger or self._setup_logger()

        # Criar toolkit de vendas
        self.sales_toolkit = SalesToolkit(
            product_catalog=product_catalog,
            crm_client=crm_client
        )

        # Criar agente AGNO
        self.agent = Agent(
            name="sales_agent",
            model=OpenAIChat(id=model_id),
            description="Assistente comercial especializado em vendas B2B",
            instructions=self._get_instructions(),
            tools=[self.sales_toolkit],
            storage=SqliteDb(
                table_name="sales_conversations",
                db_file=db_path
            ),
            add_history_to_messages=True,
            num_history_messages=10,
            show_tool_calls=True,
            markdown=True
        )

        # Estatísticas
        self.stats = {
            "total_conversations": 0,
            "leads_created": 0,
            "demos_scheduled": 0,
            "products_presented": 0,
            "total_processing_time": 0.0
        }

        self.logger.info("Sales Agent initialized successfully")

    def _setup_logger(self) -> logging.Logger:
        """Configura logger para o agente."""
        logger = logging.getLogger("SalesAgent")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _get_instructions(self) -> List[str]:
        """Define instruções completas para o agente de vendas."""
        return [
            # ROLE
            "Você é um assistente de vendas especializado, consultivo e profissional.",
            "Você representa uma empresa de software B2B e ajuda potenciais clientes a encontrar a solução ideal.",

            # RESPONSABILIDADES
            "Suas responsabilidades são:",
            "1. Entender a necessidade do cliente através de perguntas qualificadoras",
            "2. Qualificar leads usando metodologia BANT (Budget, Authority, Need, Timeline)",
            "3. Apresentar produtos relevantes do catálogo",
            "4. Responder dúvidas e tratar objeções de forma consultiva",
            "5. Capturar informações de contato (nome, email, empresa)",
            "6. Agendar demonstrações e próximos passos",

            # PERSONALITY
            "Seu estilo de comunicação:",
            "- Consultivo e educativo (não agressivo ou insistente)",
            "- Focado em entender necessidades antes de apresentar soluções",
            "- Transparente sobre capacidades e limitações dos produtos",
            "- Profissional mas acessível e empático",
            "- Direto e objetivo (evite respostas muito longas)",

            # CONSTRAINTS
            "Restrições importantes:",
            "- NUNCA invente informações sobre produtos ou funcionalidades",
            "- NUNCA prometa recursos que não existem no catálogo",
            "- NÃO dê descontos acima de 5% sem aprovação (informe que precisa consultar gestor)",
            "- NÃO compartilhe informações de outros clientes",
            "- SEMPRE use as ferramentas disponíveis para buscar informações de produtos",
            "- SEMPRE capture email antes de enviar materiais ou agendar demos",

            # PROCESSO DE QUALIFICAÇÃO (BANT)
            "Para qualificar leads, identifique sutilmente:",
            "- Budget: Qual investimento mensal está previsto? Há orçamento aprovado?",
            "- Authority: Quem toma a decisão de compra? Precisa de aprovação?",
            "- Need: Qual o problema principal? Qual impacto se não resolver?",
            "- Timeline: Qual a urgência? Quando precisam da solução funcionando?",

            # FLUXO DE CONVERSA
            "Fluxo ideal da conversa:",
            "1. Cumprimente e pergunte como pode ajudar",
            "2. Faça 2-3 perguntas qualificadoras para entender o contexto",
            "3. Use search_products para encontrar soluções relevantes",
            "4. Apresente 1-2 produtos mais adequados com get_product_details",
            "5. Responda dúvidas e trate objeções de forma consultiva",
            "6. Capture informações com create_lead quando apropriado",
            "7. Ofereça agendar demo com schedule_demo",

            # TRATAMENTO DE OBJEÇÕES
            "Ao tratar objeções:",
            "1. Valide a preocupação do cliente ('Entendo sua preocupação sobre...')",
            "2. Reframe positivamente ('Nossos clientes no início também pensavam isso...')",
            "3. Forneça evidência ou exemplo concreto",
            "4. Faça pergunta de follow-up para entender melhor",

            # FORMAT
            "Formato das respostas:",
            "- Respostas concisas (2-4 frases quando possível)",
            "- Faça UMA pergunta por vez (evite múltiplas perguntas)",
            "- Use markdown para listas quando apresentar features/benefícios",
            "- Seja empático e positivo sempre",

            # FERRAMENTAS
            "Use as ferramentas disponíveis:",
            "- search_products: Para buscar produtos por termo ou categoria",
            "- get_product_details: Para mostrar detalhes completos de um produto",
            "- check_product_availability: Para verificar disponibilidade",
            "- calculate_pricing: Para calcular preço personalizado",
            "- create_lead: Para registrar lead no CRM (após capturar nome e email)",
            "- schedule_demo: Para agendar demonstração",
        ]

    def process(
        self,
        message: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Processa mensagem do usuário.

        Args:
            message: Mensagem do usuário
            session_id: ID da sessão (será gerado se não fornecido)
            user_id: ID do usuário (opcional)
            metadata: Metadados adicionais (opcional)

        Returns:
            Dict com resposta e informações
        """
        start_time = datetime.utcnow()

        try:
            # Validar input
            if not message or not message.strip():
                return {
                    "success": False,
                    "error": "Mensagem vazia",
                    "response": "Por favor, envie uma mensagem."
                }

            # Gerar session_id se necessário
            if not session_id:
                session_id = f"session_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

            # Processar com AGNO
            response = self.agent.run(
                message,
                session_id=session_id,
                stream=False
            )

            # Extrair resposta
            response_text = str(response.content) if hasattr(response, 'content') else str(response)

            # Métricas
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Atualizar estatísticas
            self.stats["total_conversations"] += 1
            self.stats["total_processing_time"] += processing_time

            # Detectar ações (simplificado - AGNO rastreia tool calls automaticamente)
            if "create_lead" in str(response_text).lower():
                self.stats["leads_created"] += 1
            if "schedule_demo" in str(response_text).lower():
                self.stats["demos_scheduled"] += 1

            # Log
            self.logger.info(
                f"Message processed - Session: {session_id}, "
                f"User: {user_id or 'anonymous'}, "
                f"Time: {processing_time:.2f}s"
            )

            return {
                "success": True,
                "response": response_text,
                "session_id": session_id,
                "metadata": {
                    "processing_time_ms": processing_time * 1000,
                    "user_id": user_id,
                    "timestamp": start_time.isoformat(),
                    **(metadata or {})
                }
            }

        except Exception as e:
            self.logger.error(f"Error processing message: {e}", exc_info=True)

            return {
                "success": False,
                "error": str(e),
                "response": "Desculpe, ocorreu um erro. Pode repetir sua pergunta?"
            }

    def qualify_lead(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Analisa conversa e retorna qualificação do lead (BANT score).

        Args:
            session_id: ID da sessão para analisar

        Returns:
            Dict com qualificação do lead
        """
        try:
            # Aqui você implementaria análise da conversa
            # Para simplificar, retornamos exemplo
            # Em produção, consultaria histórico e usaria LLM para análise

            return {
                "session_id": session_id,
                "bant_score": {
                    "budget": "unknown",  # low|medium|high|unknown
                    "authority": "unknown",  # decision_maker|influencer|user|unknown
                    "need": "unclear",  # critical|important|nice_to_have|unclear
                    "timeline": "unknown"  # immediate|1-3m|3-6m|6m+|unknown
                },
                "overall_score": 0,  # 0-100
                "fit": "unknown",  # excellent|good|moderate|poor|unknown
                "recommended_action": "continue_conversation",
                "notes": "Necessário mais informações para qualificação completa"
            }

        except Exception as e:
            self.logger.error(f"Error qualifying lead: {e}")
            return {"error": str(e)}

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do agente."""
        total = self.stats["total_conversations"]
        return {
            **self.stats,
            "avg_processing_time": (
                self.stats["total_processing_time"] / total
                if total > 0 else 0
            )
        }


# ==================== Exemplo de Uso ====================

if __name__ == "__main__":
    """
    Exemplo completo de uso do Sales Agent com AGNO.
    """
    import os

    print("=" * 80)
    print("Sales Agent com AGNO Framework - Exemplo de Uso")
    print("=" * 80)

    # Verificar se tem API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\nAVISO: Configure OPENAI_API_KEY no ambiente para executar este exemplo")
        print("export OPENAI_API_KEY='sua-chave-aqui'\n")
        exit(1)

    # Criar agente
    print("\n1. Inicializando Sales Agent...")
    agent = SalesAgent(
        model_id="gpt-4",
        db_path="/tmp/sales_agent_example.db"
    )
    print("✓ Agente inicializado com sucesso")

    # Simular conversa
    session_id = "demo_session_001"

    print("\n2. Simulando conversa de vendas...")
    print("-" * 80)

    # Mensagem 1: Início da conversa
    print("\nUsuário: Olá, gostaria de saber sobre soluções de CRM")
    result1 = agent.process(
        message="Olá, gostaria de saber sobre soluções de CRM",
        session_id=session_id,
        user_id="user_001"
    )
    print(f"Agente: {result1['response']}")
    print(f"[Tempo: {result1['metadata']['processing_time_ms']:.0f}ms]")

    # Mensagem 2: Fornecer contexto
    print("\n" + "-" * 80)
    print("\nUsuário: Somos uma empresa de tecnologia com 150 funcionários. "
          "Nosso time de vendas tem 25 pessoas e estamos com dificuldade "
          "para organizar o pipeline.")
    result2 = agent.process(
        message="Somos uma empresa de tecnologia com 150 funcionários. "
                "Nosso time de vendas tem 25 pessoas e estamos com dificuldade "
                "para organizar o pipeline.",
        session_id=session_id,
        user_id="user_001"
    )
    print(f"Agente: {result2['response']}")
    print(f"[Tempo: {result2['metadata']['processing_time_ms']:.0f}ms]")

    # Mensagem 3: Pedir demonstração
    print("\n" + "-" * 80)
    print("\nUsuário: Parece interessante! Meu nome é Carlos Silva, "
          "email carlos.silva@empresa.com.br. "
          "Gostaria de agendar uma demo para próxima semana.")
    result3 = agent.process(
        message="Parece interessante! Meu nome é Carlos Silva, "
                "email carlos.silva@empresa.com.br. "
                "Gostaria de agendar uma demo para próxima semana.",
        session_id=session_id,
        user_id="user_001"
    )
    print(f"Agente: {result3['response']}")
    print(f"[Tempo: {result3['metadata']['processing_time_ms']:.0f}ms]")

    # Ver estatísticas
    print("\n" + "=" * 80)
    print("3. Estatísticas do Agente")
    print("-" * 80)
    stats = agent.get_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    # Informações adicionais
    print("\n" + "=" * 80)
    print("4. Próximos Passos")
    print("-" * 80)
    print("""
Para usar em produção:

1. Configuração:
   - Use PostgreSQL ao invés de SQLite
   - Configure logging centralizado (DataDog, CloudWatch)
   - Implemente monitoramento de métricas

2. Integrações:
   - Integre com CRM real (Salesforce, HubSpot, Pipedrive)
   - Configure webhooks para notificações
   - Adicione sistema de calendário (Calendly, Google Calendar)

3. Otimizações:
   - Implemente caching de catálogo de produtos
   - Adicione rate limiting
   - Configure auto-scaling

4. Qualidade:
   - Crie testes automatizados
   - Implemente A/B testing de prompts
   - Configure alertas de anomalias

5. Compliance:
   - Adicione validações de LGPD
   - Implemente audit log
   - Configure backup de conversas
    """)

    print("\n" + "=" * 80)
    print("Exemplo concluído!")
    print("=" * 80)
