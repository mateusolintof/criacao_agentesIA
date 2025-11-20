"""
Exemplo: Simple Chatbot com AGNO

Um chatbot simples com um único agente usando o framework AGNO.
Demonstra o uso básico de AGNO Agent com memória persistente.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import re

# Imports do AGNO
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb

from agent_config import AGENT_CONFIG
from prompts import PROMPTS

# Carregar variáveis de ambiente
load_dotenv()


class SimpleChatbot:
    """
    Wrapper para AGNO Agent com funcionalidades adicionais.

    Adiciona:
    - Validação de inputs
    - Guardrails para outputs
    - Estatísticas de uso
    - Error handling robusto
    """

    def __init__(self, db_path: str = "/tmp/simple_chatbot.db"):
        """
        Inicializa o chatbot AGNO.

        Args:
            db_path: Caminho para banco de dados SQLite
        """
        # Criar agente AGNO
        self.agent = Agent(
            name="simple_chatbot",
            model=OpenAIChat(id=AGENT_CONFIG["model"]),
            description="Assistente virtual amigável para atendimento ao cliente",
            instructions=PROMPTS["instructions"],
            storage=SqliteDb(
                table_name="chatbot_sessions",
                db_file=db_path
            ),
            add_history_to_messages=True,
            num_history_messages=AGENT_CONFIG.get("num_history_messages", 10),
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

    def validate_input(self, message: str) -> tuple[bool, str]:
        """
        Valida input do usuário.

        Args:
            message: Mensagem do usuário

        Returns:
            Tuple (is_valid, error_message)
        """
        if not message or not message.strip():
            return False, "mensagem vazia não é permitida"

        if len(message) > AGENT_CONFIG.get("max_input_length", 2000):
            return False, f"mensagem muito longa (máximo {AGENT_CONFIG['max_input_length']} caracteres)"

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
                return False, "input contém padrões não permitidos"

        return True, ""

    def apply_guardrails(self, response: str) -> tuple[str, bool]:
        """
        Aplica guardrails à resposta gerada.

        Args:
            response: Resposta do agente

        Returns:
            Tuple (resposta_filtrada, passou_guardrails)
        """
        if not AGENT_CONFIG.get("enable_guardrails", True):
            return response, True

        # Verificar informações sensíveis
        sensitive_patterns = [
            r'\d{3}\.\d{3}\.\d{3}-\d{2}',  # CPF
            r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}',  # CNPJ
            r'\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}',  # Cartão
        ]

        for pattern in sensitive_patterns:
            if re.search(pattern, response):
                return (
                    "Desculpe, não posso compartilhar informações sensíveis. "
                    "Como posso ajudar de outra forma?",
                    False
                )

        return response, True

    def process(self, message: str, session_id: str = None) -> dict:
        """
        Processa mensagem do usuário.

        Args:
            message: Mensagem do usuário
            session_id: ID da sessão (opcional)

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
                    "response": f"Desculpe, {error_msg}"
                }

            # 2. Gerar session_id se não fornecido
            if not session_id:
                session_id = f"session_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

            # 3. Executar agente AGNO
            response = self.agent.run(
                message,
                session_id=session_id,
                stream=False
            )

            # 4. Extrair resposta
            response_text = str(response.content) if hasattr(response, 'content') else str(response)

            # 5. Aplicar guardrails
            filtered_response, passed = self.apply_guardrails(response_text)

            # 6. Calcular métricas
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # 7. Atualizar estatísticas
            self.stats["total_interactions"] += 1
            self.stats["successful_interactions"] += 1
            self.stats["total_processing_time"] += processing_time

            # 8. Retornar resposta
            return {
                "success": True,
                "response": filtered_response,
                "session_id": session_id,
                "metadata": {
                    "processing_time_ms": processing_time * 1000,
                    "passed_guardrails": passed,
                    "timestamp": start_time.isoformat()
                }
            }

        except Exception as e:
            self.stats["failed_interactions"] += 1
            return {
                "success": False,
                "error": str(e),
                "response": "Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente."
            }

    def get_stats(self) -> dict:
        """Retorna estatísticas do agente."""
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


def print_welcome():
    """Imprime mensagem de boas-vindas."""
    print("\n" + "="*60)
    print("  CHATBOT SIMPLES - AGNO Framework")
    print("="*60)
    print("\nDigite suas mensagens e pressione Enter.")
    print("Para sair, digite 'sair' ou 'quit'.\n")


def main():
    """Função principal."""
    # Verificar API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Erro: OPENAI_API_KEY não configurada.")
        print("Configure no arquivo .env (veja .env.example)")
        sys.exit(1)

    # Inicializar componentes
    print("Inicializando chatbot AGNO...")

    # Criar agente AGNO
    agent = SimpleChatbot(db_path="/tmp/simple_chatbot.db")

    print("Chatbot pronto!\n")
    print_welcome()

    # Session ID para o usuário demo
    session_id = "demo_session"

    # Loop de conversação
    while True:
        try:
            # Input do usuário
            user_input = input("Você: ").strip()

            # Verificar saída
            if user_input.lower() in ["sair", "quit", "exit", "q"]:
                print("\nEncerrando conversa. Até logo!")

                # Mostrar estatísticas
                stats = agent.get_stats()
                print(f"\nEstatísticas da sessão:")
                print(f"   - Mensagens: {stats['total_interactions']}")
                print(f"   - Taxa de sucesso: {stats['success_rate']*100:.1f}%")
                print(f"   - Tempo médio: {stats['avg_processing_time']:.2f}s\n")
                break

            # Validar input não vazio
            if not user_input:
                continue

            # Processar com agente
            result = agent.process(user_input, session_id=session_id)

            # Exibir resposta
            if result["success"]:
                print(f"Agente: {result['response']}\n")
            else:
                print(f"Erro: {result.get('error', 'Erro desconhecido')}\n")

        except KeyboardInterrupt:
            print("\n\nInterrompido pelo usuário. Até logo!")
            break

        except Exception as e:
            print(f"\nErro inesperado: {e}")
            print("Continuando...\n")


if __name__ == "__main__":
    main()
