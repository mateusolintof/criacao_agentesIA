"""
Configuração do Simple Chatbot - AGNO

Configurações específicas para o agente AGNO.
"""

AGENT_CONFIG = {
    # Modelo LLM
    "model": "gpt-4o",  # Atualizado para GPT-4o (Nov 2025)

    # Memória e contexto
    "num_history_messages": 10,  # Número de mensagens históricas no contexto

    # Validações
    "max_input_length": 2000,  # Máximo de caracteres no input
    "enable_guardrails": True,  # Ativar validações de segurança

    # Modo de operação
    "verbose": True,  # Logs detalhados
    "markdown": True,  # Respostas formatadas em markdown
}
