"""
Definição de Tasks para o Sistema Multi-Agent

Tasks representam trabalhos que os agentes devem executar.
No processo hierárquico, o Manager coordena a execução.
"""

from crewai import Task, Agent
from typing import Dict


def create_routing_task(message: str, agent: Agent) -> Task:
    """
    Cria tarefa de roteamento (Manager identifica intenção).

    Args:
        message: Mensagem do usuário
        agent: Agente Manager

    Returns:
        Task configurada
    """
    return Task(
        description=f"""Analise a seguinte mensagem do cliente e identifique qual
        agente especializado deve responder:

        MENSAGEM DO CLIENTE:
        {message}

        AGENTES DISPONÍVEIS:
        - sales: Para questões de vendas, preços, propostas, qualificação
        - support: Para problemas técnicos, configuração, bugs, troubleshooting
        - product: Para informações sobre features, comparações, casos de uso

        Identifique a intenção principal e retorne APENAS o nome do agente adequado
        (sales, support ou product) seguido de uma breve justificativa (1 linha).

        Formato da resposta:
        AGENTE: [nome do agente]
        RAZÃO: [breve justificativa]""",
        agent=agent,
        expected_output="Nome do agente (sales/support/product) e justificativa"
    )


def create_response_task(
    message: str,
    context: Task,
    agents: Dict[str, Agent]
) -> Task:
    """
    Cria tarefa de resposta (agente especializado responde).

    Esta task será executada pelo agente apropriado baseado no
    roteamento feito pela task anterior.

    Args:
        message: Mensagem original do usuário
        context: Task de roteamento (para contexto)
        agents: Dicionário com agentes disponíveis

    Returns:
        Task configurada
    """
    # No processo hierárquico, o Manager delegará automaticamente
    # Escolhemos o sales como default, mas o manager pode delegar para qualquer um
    return Task(
        description=f"""Com base no roteamento definido, responda a seguinte mensagem
        do cliente de forma completa e profissional:

        MENSAGEM DO CLIENTE:
        {message}

        INSTRUÇÕES:
        1. Seja específico e útil na resposta
        2. Use informações precisas sobre produtos/preços/features
        3. Se for vendas: qualifique e apresente soluções
        4. Se for suporte: diagnostique e forneça soluções passo a passo
        5. Se for produto: explique features e benefícios claramente
        6. Mantenha tom profissional mas acessível
        7. Pergunte se há mais dúvidas ao final

        Forneça uma resposta completa e natural, como se estivesse em uma
        conversa real com o cliente.""",
        agent=agents["sales"],  # Default, mas manager pode delegar
        expected_output="Resposta completa e profissional para o cliente",
        context=[context]  # Usa o roteamento como contexto
    )


def create_qualification_task(message: str, agent: Agent) -> Task:
    """
    Cria tarefa de qualificação de lead (Sales).

    Args:
        message: Mensagem do usuário
        agent: Agente de vendas

    Returns:
        Task configurada
    """
    return Task(
        description=f"""Qualifique o lead com base na mensagem:

        MENSAGEM:
        {message}

        CRITÉRIOS DE QUALIFICAÇÃO:
        - Tamanho da empresa (estimado)
        - Necessidades identificadas
        - Urgência (explícita ou implícita)
        - Budget potencial
        - Fit com nossos produtos

        Faça perguntas de qualificação se necessário e sugira o próximo passo
        (demo, trial, proposta, etc).""",
        agent=agent,
        expected_output="Análise de qualificação e próximos passos sugeridos"
    )


def create_troubleshooting_task(message: str, agent: Agent) -> Task:
    """
    Cria tarefa de troubleshooting (Support).

    Args:
        message: Descrição do problema
        agent: Agente de suporte

    Returns:
        Task configurada
    """
    return Task(
        description=f"""Diagnostique e resolva o seguinte problema técnico:

        PROBLEMA REPORTADO:
        {message}

        PROCESSO:
        1. Identificar sintomas e possível causa raiz
        2. Solicitar informações adicionais se necessário
        3. Fornecer solução passo a passo
        4. Mencionar como prevenir o problema no futuro
        5. Oferecer documentação relevante

        Se o problema requer investigação mais profunda, explique o processo
        de escalação.""",
        agent=agent,
        expected_output="Diagnóstico e solução passo a passo"
    )


def create_product_comparison_task(message: str, agent: Agent) -> Task:
    """
    Cria tarefa de comparação de produtos (Product).

    Args:
        message: Mensagem solicitando comparação
        agent: Agente de produto

    Returns:
        Task configurada
    """
    return Task(
        description=f"""Compare produtos ou explique features com base na solicitação:

        SOLICITAÇÃO:
        {message}

        INFORMAÇÕES A INCLUIR:
        - Features principais de cada produto relevante
        - Diferenças chave entre opções
        - Casos de uso ideais para cada um
        - Preços e planos disponíveis
        - Recomendação baseada em necessidades mencionadas

        Use exemplos concretos e seja claro nas comparações.""",
        agent=agent,
        expected_output="Comparação detalhada com recomendação"
    )
