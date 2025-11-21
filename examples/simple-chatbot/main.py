"""
Exemplo: Simple Chatbot com AGNO

Um chatbot simples usando AGNO para demonstrar os conceitos básicos.
Atualizado em: 2025-11-20
"""

import os
import sys
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb

# Carregar variáveis de ambiente
load_dotenv()


def print_welcome():
    """Imprime mensagem de boas-vindas."""
    print("\n" + "="*60)
    print("🤖  CHATBOT SIMPLES - AGNO Framework")
    print("="*60)
    print("\nDigite suas mensagens e pressione Enter.")
    print("Para sair, digite 'sair' ou 'quit'.\n")


def main():
    """Função principal."""
    # Verificar API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Erro: OPENAI_API_KEY não configurada.")
        print("Configure no arquivo .env (veja .env.example)")
        sys.exit(1)

    print("Inicializando chatbot com AGNO...")

    # Configurar banco de dados para memória persistente
    db = SqliteDb(
        session_table="chatbot_sessions",
        db_file="./tmp/chatbot_memory.db"
    )

    # Instruções do agente (lista de strings para AGNO)
    instructions = [
        "Você é um assistente virtual amigável e prestativo de uma empresa de software B2B.",
        "Seu objetivo é ajudar clientes com informações sobre produtos e serviços.",
        "Produtos principais:",
        "- CRM Enterprise (R$ 199/mês) - Gestão de vendas e relacionamento",
        "- AI Assistant (R$ 499/mês) - Automação com IA",
        "- Analytics Suite (R$ 299/mês) - Business Intelligence",
        "Seja sempre:",
        "- Amigável mas profissional",
        "- Consultivo (faça perguntas para entender necessidades)",
        "- Conciso (2-4 frases por resposta)",
        "- Honesto sobre limitações",
        "NUNCA invente informações sobre produtos ou preços.",
    ]

    # Criar agente AGNO
    agent = Agent(
        name="Chatbot Comercial",
        model=OpenAIChat(
            id=os.getenv("OPENAI_MODEL", "gpt-4-turbo"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
        ),
        db=db,
        add_history_to_context=True,
        num_history_runs=int(os.getenv("AGNO_NUM_HISTORY_RUNS", "5")),
        instructions=instructions,
        markdown=True,
        show_tool_calls=False,
    )

    print("✅ Chatbot pronto!\n")
    print_welcome()

    # ID da sessão (simula um usuário)
    session_id = "demo-session-001"

    # Contador de interações
    interaction_count = 0

    # Loop de conversação
    while True:
        try:
            # Input do usuário
            user_input = input("👤 Você: ").strip()

            # Verificar saída
            if user_input.lower() in ["sair", "quit", "exit", "q"]:
                print("\n👋 Encerrando conversa. Até logo!")
                print(f"\n📊 Total de mensagens: {interaction_count}\n")
                break

            # Validar input não vazio
            if not user_input:
                continue

            interaction_count += 1

            # Processar com agente AGNO
            print("🤖 Agente: ", end="", flush=True)
            
            # Usar run() com session_id para manter contexto
            response = agent.run(user_input, session_id=session_id, stream=True)
            
            print("\n")  # Nova linha após resposta

        except KeyboardInterrupt:
            print("\n\n👋 Interrompido pelo usuário. Até logo!")
            break

        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            print("Continuando...\n")


if __name__ == "__main__":
    main()
