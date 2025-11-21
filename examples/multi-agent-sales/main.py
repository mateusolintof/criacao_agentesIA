"""
Exemplo: Sistema Multi-Agente de Vendas com CrewAI

Sistema completo com múltiplos agentes especializados trabalhando em equipe.
Framework: CrewAI (Hierarchical Process)
Atualizado: 2025-11-20
"""

import os
import sys
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

# Carregar variáveis de ambiente
load_dotenv()


def create_agents():
    """Cria os agentes especializados."""
    
    # LLM compartilhado (pode usar diferentes para cada agente)
    llm = LLM(model=os.getenv("OPENAI_MODEL", "gpt-4-turbo"))
    
    # Manager Agent - Coordena a equipe (apenas em hierarchical)
    manager = Agent(
        role="Gerente de Atendimento",
        goal="Coordenar a equipe para fornecer o melhor atendimento ao cliente",
        backstory="""Você é um gerente experiente que coordena uma equipe de 
        especialistas. Analisa a necessidade do cliente e delega para o agente 
        mais adequado: vendas, suporte técnico ou informações de produto.""",
        allow_delegation=True,  # Pode delegar para outros agentes
        verbose=True,
        llm=llm
    )
    
    # Sales Agent - Especialista em vendas
    sales_agent = Agent(
        role="Consultor de Vendas",
        goal="Qualificar leads e apresentar soluções de forma consultiva",
        backstory="""Você é um consultor de vendas B2B experiente. Especialista em 
        metodologia BANT (Budget, Authority, Need, Timeline). Faz perguntas 
        inteligentes para entender necessidades e apresenta soluções relevantes.
        
        Produtos:
        - CRM Enterprise (R$ 199/usuário/mês) - Gestão de vendas
        - AI Assistant (R$ 499/mês) - Automação com IA
        - Analytics Suite (R$ 299/mês) - Business Intelligence
        
        Seja consultivo, não agressivo. Qualifique antes de apresentar.""",
        allow_delegation=False,  # Foca em sua especialidade
        verbose=True,
        llm=llm
    )
    
    # Support Agent - Especialista em suporte técnico
    support_agent = Agent(
        role="Especialista em Suporte",
        goal="Resolver dúvidas técnicas e problemas dos clientes",
        backstory="""Você é um especialista técnico com profundo conhecimento dos 
        nossos produtos. Ajuda clientes com:
        - Dúvidas sobre funcionalidades
        - Configuração e integração
        - Troubleshooting
        - Boas práticas de uso
        
        Seja claro, técnico mas acessível. Use exemplos práticos.""",
        allow_delegation=False,
        verbose=True,
        llm=llm
    )
    
    # Product Agent - Especialista em produtos
    product_agent = Agent(
        role="Especialista em Produtos",
        goal="Fornecer informações detalhadas sobre produtos e funcionalidades",
        backstory="""Você é um especialista em nosso catálogo de produtos. Conhece 
        profundamente todas as funcionalidades, casos de uso, e comparações entre 
        produtos. Ajuda clientes a entender:
        - Recursos e funcionalidades de cada produto
        - Casos de uso ideais
        - Comparações entre produtos
        - Roadmap e novidades
        
        Seja detalhado e use exemplos concretos.""",
        allow_delegation=False,
        verbose=True,
        llm=llm
    )
    
    return manager, sales_agent, support_agent, product_agent


def create_task(user_input: str, manager: Agent):
    """
    Cria a tarefa principal que será delegada pelo manager.
    
    Args:
        user_input: Mensagem do usuário
        manager: Agente manager que coordenará
    """
    task = Task(
        description=f"""Atenda a seguinte solicitação do cliente de forma completa:
        
        "{user_input}"
        
        Passos:
        1. Analise a necessidade do cliente
        2. Identifique qual especialista (vendas, suporte ou produto) é mais adequado
        3. Delegue para o agente apropriado
        4. Garanta que a resposta seja completa e útil
        5. Se necessário, coordene múltiplos especialistas
        
        A resposta deve ser profissional, clara e resolver completamente a necessidade.""",
        expected_output="""Uma resposta completa e profissional que atenda a 
        necessidade do cliente, incluindo toda informação relevante e próximos passos.""",
        agent=manager  # Manager coordena e delega
    )
    
    return task


def main():
    """Função principal."""
    
    # Verificar API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Erro: OPENAI_API_KEY não configurada.")
        print("Configure no arquivo .env")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("🤖  SISTEMA MULTI-AGENTE - CrewAI (Hierarchical)")
    print("="*70)
    print("\nEquipe de Agentes:")
    print("  👔 Gerente de Atendimento (coordena a equipe)")
    print("  💼 Consultor de Vendas (qualificação e vendas)")
    print("  🔧 Especialista em Suporte (ajuda técnica)")
    print("  📦 Especialista em Produtos (informações detalhadas)")
    print("\nDigite 'sair' para encerrar.\n")
    
    # Criar agentes
    print("Inicializando equipe de agentes...")
    manager, sales, support, product = create_agents()
    
    # Criar crew com processo hierárquico
    crew = Crew(
        agents=[manager, sales, support, product],
        tasks=[],  # Tasks serão adicionadas dinamicamente
        process=Process.hierarchical,  # Manager coordena
        manager_llm=os.getenv("CREWAI_MANAGER_LLM", "gpt-4-turbo"),
        verbose=True,
        planning=True,  # Ativa planejamento
    )
    
    print("✅ Equipe pronta!\n")
    
    # Loop de conversação
    while True:
        try:
            # Input do usuário
            user_input = input("👤 Você: ").strip()
            
            # Verificar saída
            if user_input.lower() in ["sair", "quit", "exit", "q"]:
                print("\n👋 Encerrando. Até logo!")
                break
            
            if not user_input:
                continue
            
            # Criar tarefa para esta interação
            task = create_task(user_input, manager)
            
            # Atualizar crew com nova tarefa
            crew.tasks = [task]
            
            print("\n🤖 Processando com a equipe...\n")
            print("-" * 70)
            
            # Executar crew
            result = crew.kickoff()
            
            print("-" * 70)
            print(f"\n✅ Resposta da Equipe:\n")
            print(result.raw)
            print("\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrompido. Até logo!")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            print("Continuando...\n")


if __name__ == "__main__":
    main()
