"""
Template: AGNO Base Agent

Template básico para criar agentes usando o framework AGNO.
Este arquivo serve como referência e ponto de partida para novos agentes.

AGNO (Agentic Framework) é um framework moderno para criação de agentes de IA
com suporte nativo a:
- Memória persistente (SQLite, PostgreSQL)
- Ferramentas/Tools extensíveis
- Múltiplos modelos LLM (OpenAI, Anthropic, etc)
- Session management
- Guardrails e validações
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Imports do AGNO framework
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb
from agno.tools.toolkit import Toolkit


# ==================== Exemplo 1: Agente Simples ====================

def create_simple_agent() -> Agent:
    """
    Cria um agente simples sem memória ou ferramentas.

    Use este padrão para:
    - Protótipos rápidos
    - Agentes stateless
    - Casos de uso simples (FAQ, consultas pontuais)

    Returns:
        Agent configurado
    """
    agent = Agent(
        name="simple_agent",
        model=OpenAIChat(id="gpt-4"),
        description="Agente simples para responder perguntas",
        instructions=[
            "Você é um assistente prestativo e profissional",
            "Seja conciso e direto nas respostas",
            "Se não souber algo, admita claramente"
        ],
        markdown=True  # Formata respostas em markdown
    )

    return agent


# ==================== Exemplo 2: Agente com Memória ====================

def create_agent_with_memory(
    db_path: str = "/tmp/agno_agent.db"
) -> Agent:
    """
    Cria um agente com memória persistente usando SQLite.

    A memória permite que o agente:
    - Lembre de conversas anteriores
    - Mantenha contexto entre sessões
    - Aprenda preferências do usuário

    Use este padrão para:
    - Assistentes conversacionais
    - Agentes que precisam de contexto histórico
    - Aplicações multi-sessão

    Args:
        db_path: Caminho para o arquivo SQLite de memória

    Returns:
        Agent com memória configurada
    """
    agent = Agent(
        name="memory_agent",
        model=OpenAIChat(id="gpt-4"),
        description="Agente com memória persistente",
        instructions=[
            "Você é um assistente que lembra de conversas anteriores",
            "Use o contexto histórico para fornecer respostas personalizadas",
            "Refira-se a informações mencionadas anteriormente quando relevante"
        ],
        # Configurar banco de dados SQLite para memória
        storage=SqliteDb(
            table_name="agent_sessions",
            db_file=db_path
        ),
        # Adicionar memória ao contexto do agente
        add_history_to_messages=True,
        num_history_messages=10,  # Últimas 10 mensagens no contexto
        markdown=True
    )

    return agent


# ==================== Exemplo 3: Toolkit Customizado ====================

class CustomToolkit(Toolkit):
    """
    Toolkit customizado com ferramentas específicas do negócio.

    Toolkits agrupam ferramentas relacionadas que o agente pode usar.
    Cada método decorado com @tool se torna uma ferramenta disponível.
    """

    def __init__(self):
        super().__init__(name="custom_toolkit")

    def search_database(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Busca informações no banco de dados.

        Args:
            query: Termo de busca
            limit: Número máximo de resultados (default: 5)

        Returns:
            Dict com resultados da busca
        """
        # Implementação simulada
        # Em produção, faria query real no banco
        return {
            "query": query,
            "results": [
                {"id": 1, "title": f"Resultado para {query}"},
                {"id": 2, "title": f"Outro resultado"}
            ],
            "total": 2,
            "limit": limit
        }

    def calculate_discount(
        self,
        original_price: float,
        discount_percent: float
    ) -> Dict[str, float]:
        """
        Calcula preço com desconto.

        Args:
            original_price: Preço original em reais
            discount_percent: Percentual de desconto (0-100)

        Returns:
            Dict com cálculos de desconto
        """
        if discount_percent < 0 or discount_percent > 100:
            raise ValueError("Desconto deve estar entre 0 e 100")

        discount_amount = original_price * (discount_percent / 100)
        final_price = original_price - discount_amount

        return {
            "original_price": original_price,
            "discount_percent": discount_percent,
            "discount_amount": discount_amount,
            "final_price": final_price,
            "savings": discount_amount
        }

    def validate_email(self, email: str) -> Dict[str, Any]:
        """
        Valida formato de email.

        Args:
            email: Endereço de email para validar

        Returns:
            Dict com resultado da validação
        """
        import re

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = bool(re.match(pattern, email))

        return {
            "email": email,
            "is_valid": is_valid,
            "message": "Email válido" if is_valid else "Email inválido"
        }


def create_agent_with_tools(
    db_path: str = "/tmp/agno_agent.db"
) -> Agent:
    """
    Cria um agente com ferramentas customizadas.

    Ferramentas permitem que o agente:
    - Execute ações (criar registros, enviar emails, etc)
    - Busque informações (consultar APIs, bancos de dados)
    - Faça cálculos e validações

    Use este padrão para:
    - Agentes que precisam interagir com sistemas externos
    - Automação de processos
    - Integração com APIs e serviços

    Args:
        db_path: Caminho para o arquivo SQLite de memória

    Returns:
        Agent com ferramentas configuradas
    """
    # Criar toolkit
    toolkit = CustomToolkit()

    agent = Agent(
        name="tool_agent",
        model=OpenAIChat(id="gpt-4"),
        description="Agente com ferramentas customizadas",
        instructions=[
            "Você é um assistente que pode usar ferramentas para ajudar o usuário",
            "Use as ferramentas disponíveis sempre que necessário",
            "Explique o que você está fazendo ao usar uma ferramenta",
            "Se uma ferramenta falhar, tente alternativas ou peça mais informações"
        ],
        tools=[toolkit],  # Adicionar toolkit
        storage=SqliteDb(
            table_name="tool_agent_sessions",
            db_file=db_path
        ),
        add_history_to_messages=True,
        num_history_messages=10,
        show_tool_calls=True,  # Mostrar chamadas de ferramentas na resposta
        markdown=True
    )

    return agent


# ==================== Exemplo 4: Agente Completo para Produção ====================

class ProductionAgent:
    """
    Wrapper para agente AGNO com funcionalidades adicionais para produção.

    Adiciona:
    - Logging estruturado
    - Métricas e estatísticas
    - Validação de input/output
    - Guardrails
    - Error handling robusto
    """

    def __init__(
        self,
        agent_name: str,
        model_id: str = "gpt-4",
        db_path: str = "/tmp/agno_production.db",
        tools: Optional[List[Toolkit]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Inicializa agente de produção.

        Args:
            agent_name: Nome identificador do agente
            model_id: ID do modelo LLM (gpt-4, claude-3-opus, etc)
            db_path: Caminho para banco de dados SQLite
            tools: Lista de toolkits (opcional)
            logger: Logger customizado (opcional)
        """
        self.agent_name = agent_name
        self.logger = logger or self._setup_logger()

        # Criar agente AGNO
        self.agent = Agent(
            name=agent_name,
            model=OpenAIChat(id=model_id),
            description=f"Agente de produção: {agent_name}",
            instructions=self._load_instructions(),
            tools=tools or [],
            storage=SqliteDb(
                table_name=f"{agent_name}_sessions",
                db_file=db_path
            ),
            add_history_to_messages=True,
            num_history_messages=10,
            show_tool_calls=True,
            markdown=True
        )

        # Estatísticas
        self.stats = {
            "total_interactions": 0,
            "successful_interactions": 0,
            "failed_interactions": 0,
            "total_tokens": 0,
            "total_processing_time": 0.0
        }

        self.logger.info(f"Production agent '{agent_name}' initialized")

    def _setup_logger(self) -> logging.Logger:
        """Configura logger para o agente."""
        logger = logging.getLogger(self.agent_name)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _load_instructions(self) -> List[str]:
        """
        Carrega instruções do agente.
        Sobrescreva este método para customizar instruções.
        """
        return [
            "Você é um assistente profissional e prestativo",
            "Seja claro, conciso e objetivo nas respostas",
            "Use ferramentas quando disponíveis e apropriado",
            "Se não souber algo, admita honestamente",
            "Mantenha tom profissional mas acessível"
        ]

    def validate_input(self, message: str) -> tuple[bool, Optional[str]]:
        """
        Valida input do usuário antes de processar.

        Args:
            message: Mensagem do usuário

        Returns:
            Tuple (is_valid, error_message)
        """
        # Input vazio
        if not message or not message.strip():
            return False, "Mensagem vazia"

        # Input muito longo (limite de 10k caracteres)
        if len(message) > 10000:
            return False, "Mensagem muito longa (máximo 10.000 caracteres)"

        # Detectar possível prompt injection
        malicious_patterns = [
            "ignore previous instructions",
            "ignore all previous",
            "disregard all",
            "forget everything",
            "you are now"
        ]

        message_lower = message.lower()
        for pattern in malicious_patterns:
            if pattern in message_lower:
                self.logger.warning(f"Potential prompt injection detected: {pattern}")
                return False, "Input contém padrões não permitidos"

        return True, None

    def apply_guardrails(self, response: str) -> tuple[str, bool]:
        """
        Aplica guardrails à resposta gerada.

        Args:
            response: Resposta do agente

        Returns:
            Tuple (resposta_filtrada, passou_guardrails)
        """
        # Verificar informações sensíveis (exemplo simples)
        sensitive_patterns = [
            r'\d{3}\.\d{3}\.\d{3}-\d{2}',  # CPF
            r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}',  # CNPJ
            r'\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}',  # Cartão de crédito
        ]

        import re
        for pattern in sensitive_patterns:
            if re.search(pattern, response):
                self.logger.warning("Sensitive information detected in response")
                return (
                    "Desculpe, não posso compartilhar informações sensíveis. "
                    "Como posso ajudar de outra forma?",
                    False
                )

        return response, True

    def process(
        self,
        message: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processa mensagem do usuário e retorna resposta.

        Args:
            message: Mensagem do usuário
            session_id: ID da sessão (opcional, será gerado se não fornecido)
            user_id: ID do usuário (opcional)

        Returns:
            Dict com resposta e metadados
        """
        start_time = datetime.utcnow()

        try:
            # 1. Validar input
            is_valid, error_msg = self.validate_input(message)
            if not is_valid:
                self.stats["failed_interactions"] += 1
                return {
                    "success": False,
                    "error": error_msg,
                    "response": f"Erro: {error_msg}"
                }

            # 2. Preparar contexto de sessão
            if not session_id:
                session_id = f"session_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

            # 3. Executar agente AGNO
            # No AGNO, usamos run() ou print_response() para processar
            response = self.agent.run(
                message,
                session_id=session_id,
                stream=False  # Set True para streaming
            )

            # 4. Extrair resposta
            # response pode ser RunResponse object
            response_text = str(response.content) if hasattr(response, 'content') else str(response)

            # 5. Aplicar guardrails
            filtered_response, passed_guardrails = self.apply_guardrails(response_text)

            # 6. Calcular métricas
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # 7. Atualizar estatísticas
            self.stats["total_interactions"] += 1
            self.stats["successful_interactions"] += 1
            self.stats["total_processing_time"] += processing_time

            # 8. Log da interação
            self.logger.info(
                f"Interaction processed - Session: {session_id}, "
                f"User: {user_id or 'anonymous'}, "
                f"Time: {processing_time:.2f}s"
            )

            # 9. Retornar resposta
            return {
                "success": True,
                "response": filtered_response,
                "session_id": session_id,
                "metadata": {
                    "processing_time_ms": processing_time * 1000,
                    "passed_guardrails": passed_guardrails,
                    "user_id": user_id,
                    "timestamp": start_time.isoformat()
                }
            }

        except Exception as e:
            self.logger.error(f"Error processing message: {e}", exc_info=True)
            self.stats["failed_interactions"] += 1

            return {
                "success": False,
                "error": str(e),
                "response": "Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente."
            }

    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do agente.

        Returns:
            Dict com métricas
        """
        total = self.stats["total_interactions"]
        return {
            **self.stats,
            "success_rate": (
                self.stats["successful_interactions"] / total
                if total > 0 else 0
            ),
            "avg_processing_time": (
                self.stats["total_processing_time"] / total
                if total > 0 else 0
            )
        }

    def reset_stats(self):
        """Reseta estatísticas do agente."""
        self.stats = {
            "total_interactions": 0,
            "successful_interactions": 0,
            "failed_interactions": 0,
            "total_tokens": 0,
            "total_processing_time": 0.0
        }
        self.logger.info("Stats reset")


# ==================== Exemplo de Uso ====================

if __name__ == "__main__":
    """
    Exemplos de uso dos diferentes padrões de agentes AGNO.
    """

    print("=" * 60)
    print("AGNO Agent Templates - Exemplos de Uso")
    print("=" * 60)

    # ========== Exemplo 1: Agente Simples ==========
    print("\n1. Agente Simples (sem memória)")
    print("-" * 60)

    simple_agent = create_simple_agent()

    # Executar com print_response para ver output formatado
    # simple_agent.print_response("Olá! Como você pode me ajudar?", stream=True)

    # Ou usar run() para obter resposta programaticamente
    response1 = simple_agent.run("O que é AGNO framework?", stream=False)
    print(f"Resposta: {response1.content}")

    # ========== Exemplo 2: Agente com Memória ==========
    print("\n2. Agente com Memória")
    print("-" * 60)

    memory_agent = create_agent_with_memory(db_path="/tmp/example_memory.db")

    # Primeira conversa
    session_id = "user_123"
    response2 = memory_agent.run(
        "Meu nome é João e gosto de Python",
        session_id=session_id,
        stream=False
    )
    print(f"Primeira mensagem: {response2.content}")

    # Segunda mensagem - agente deve lembrar do nome
    response3 = memory_agent.run(
        "Qual é o meu nome?",
        session_id=session_id,
        stream=False
    )
    print(f"Segunda mensagem: {response3.content}")

    # ========== Exemplo 3: Agente com Ferramentas ==========
    print("\n3. Agente com Ferramentas")
    print("-" * 60)

    tool_agent = create_agent_with_tools(db_path="/tmp/example_tools.db")

    response4 = tool_agent.run(
        "Calcule o preço final de um produto de R$ 1000 com 15% de desconto",
        session_id="tool_session_1",
        stream=False
    )
    print(f"Resposta com ferramenta: {response4.content}")

    # ========== Exemplo 4: Agente de Produção ==========
    print("\n4. Agente de Produção (com validações e métricas)")
    print("-" * 60)

    # Criar toolkit customizado
    toolkit = CustomToolkit()

    production_agent = ProductionAgent(
        agent_name="production_example",
        model_id="gpt-4",
        db_path="/tmp/example_production.db",
        tools=[toolkit]
    )

    # Processar mensagem
    result = production_agent.process(
        message="Valide o email: contato@empresa.com.br",
        session_id="prod_session_1",
        user_id="user_456"
    )

    print(f"Sucesso: {result['success']}")
    print(f"Resposta: {result['response']}")
    print(f"Tempo de processamento: {result['metadata']['processing_time_ms']:.2f}ms")

    # Ver estatísticas
    print("\nEstatísticas do agente:")
    stats = production_agent.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("Exemplos concluídos!")
    print("=" * 60)

    # NOTAS IMPORTANTES:
    print("\nNotas de Uso:")
    print("1. Certifique-se de ter OPENAI_API_KEY configurada no ambiente")
    print("2. Instale AGNO: pip install agno")
    print("3. Para produção, use PostgreSQL ao invés de SQLite")
    print("4. Implemente logging centralizado (DataDog, CloudWatch, etc)")
    print("5. Configure monitoring de métricas e alertas")
    print("6. Adicione testes automatizados para seus agentes")
    print("7. Versionamento de prompts e instruções")
