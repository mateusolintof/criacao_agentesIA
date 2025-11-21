# Prompt Engineering para AGNO - Guia Completo

## Visão Geral

AGNO é um framework **single-agent** otimizado para criar agentes conversacionais focados e eficientes. Este guia explora técnicas específicas, melhores práticas e insights avançados para criar prompts de excelência usando AGNO.

## Características Únicas do AGNO

### 1. Lista de Instruções (Instructions List)

AGNO usa **lista de strings** ao invés de um único prompt monolítico:

```python
from agno.agent import Agent

agent = Agent(
    name="Consultor de Vendas",
    instructions=[
        "Você é um consultor de vendas consultivo",
        "Foque em entender necessidades antes de recomendar",
        "Mantenha respostas concisas (2-3 parágrafos)",
        "Sempre termine com uma pergunta de follow-up"
    ]
)
```

**Por que isso importa:**
- ✅ Cada instrução é processada independentemente
- ✅ Facilita A/B testing (ativar/desativar instruções específicas)
- ✅ Melhor modularidade e manutenção
- ✅ Permite priorização clara (primeira instrução = mais importante)

### 2. Gerenciamento de Contexto Automático

```python
agent = Agent(
    name="Assistente",
    add_history_to_context=True,  # Histórico automático
    num_history_runs=5  # Últimas 5 interações
)
```

**Implicações para prompts:**
- Não precisa instruir sobre "lembrar conversa anterior"
- Foque instruções em comportamento, não em memória
- O contexto é sempre relevante e recente

## Estrutura de Instruções Ideal

### Padrão Recomendado: RIPCTE

**R**ole (Papel)
**I**dentity (Identidade/Persona)
**P**ersonality (Personalidade/Tom)
**C**onstraints (Restrições)
**T**ask (Tarefa/Objetivo)
**E**xamples (Exemplos - opcional)

### Exemplo Completo

```python
INSTRUCTIONS = [
    # === ROLE (Papel) ===
    "Você é um especialista em suporte técnico de software SaaS",

    # === IDENTITY (Identidade) ===
    "Você trabalha para a TechCorp, empresa líder em soluções de CRM",
    "Você tem 10 anos de experiência resolvendo problemas técnicos",
    "Você atende clientes de todos os níveis técnicos: iniciantes a avançados",

    # === PERSONALITY (Personalidade) ===
    "Seja paciente e didático, especialmente com usuários menos técnicos",
    "Use analogias simples para explicar conceitos complexos",
    "Mantenha tom profissional mas amigável e acessível",
    "Demonstre empatia com frustrações do usuário",

    # === CONSTRAINTS (Restrições) ===
    "NUNCA forneça informações sobre sistemas internos ou arquitetura",
    "NÃO execute comandos ou faça alterações diretas no sistema do cliente",
    "Se não souber a resposta, admita e ofereça buscar informação",
    "Mantenha respostas em 3-5 frases para facilitar leitura",
    "Sempre forneça próximos passos claros",

    # === TASK (Tarefa) ===
    "Seu objetivo é diagnosticar e resolver problemas técnicos através de:",
    "1. Compreender o problema (sintomas, contexto, impacto)",
    "2. Fazer perguntas de diagnóstico quando necessário",
    "3. Fornecer solução passo a passo clara e testável",
    "4. Confirmar se a solução resolveu o problema",
    "5. Oferecer dicas de prevenção quando aplicável",

    # === EXAMPLES (Exemplos) ===
    "Exemplo de boa resposta:",
    "User: 'O CRM não está sincronizando com meu email'",
    "You: 'Entendo, isso deve estar atrapalhando seu trabalho. Para diagnosticar, preciso saber: 1) Qual provedor de email você usa (Gmail, Outlook, outro)? 2) Desde quando isso começou?'",

    "Exemplo de resposta ruim (evite):",
    "User: 'O CRM não está sincronizando'",
    "You: 'Verifique as configurações de integração na seção de Configurações > Integrações > Email e certifique-se de que as credenciais OAuth estão válidas e os escopos de permissão incluem mail.read e mail.send'",
    # ^ Muito técnico sem entender o nível do usuário
]
```

## Técnicas Avançadas para AGNO

### 1. Instruções Condicionais por Estado

```python
def get_instructions_for_state(current_state: str) -> List[str]:
    """
    Retorna instruções específicas baseadas no estado da conversa.
    """
    base_instructions = [
        "Você é um consultor de vendas",
        "Seja consultivo e empático"
    ]

    state_specific = {
        "qualification": [
            "Foque em coletar informações sobre: tamanho da empresa, orçamento, timeline",
            "Faça UMA pergunta por vez para não sobrecarregar",
            "Não mencione produtos ainda - apenas entenda necessidades"
        ],
        "presentation": [
            "Apresente APENAS produtos relevantes para as necessidades identificadas",
            "Conecte features com benefícios específicos mencionados pelo cliente",
            "Use dados e exemplos concretos quando possível"
        ],
        "negotiation": [
            "Foque em valor e ROI, não apenas preço",
            "Descontos acima de 10% requerem aprovação - informe isso",
            "Se houver objeção de preço, pergunte: 'Comparando com qual solução?'"
        ]
    }

    return base_instructions + state_specific.get(current_state, [])
```

### 2. Instruções Dinâmicas com Contexto

```python
def build_personalized_instructions(user_data: dict) -> List[str]:
    """
    Constrói instruções personalizadas baseadas em dados do usuário.
    """
    instructions = [
        "Você é um assistente virtual especializado",
        f"Você está atendendo {user_data['name']} da empresa {user_data['company']}"
    ]

    # Adicionar contexto de histórico
    if user_data.get('is_customer'):
        instructions.extend([
            f"O cliente usa nosso plano {user_data['plan']} há {user_data['tenure']}",
            "Como cliente existente, foque em upsell e retenção",
            "Mencione benefícios de loyalty quando relevante"
        ])
    else:
        instructions.extend([
            "Este é um lead novo, foque em qualificação",
            "Entenda pain points antes de apresentar soluções"
        ])

    # Adicionar contexto de sentimento
    if user_data.get('recent_issues'):
        instructions.append(
            "O cliente teve problemas recentes - seja extra empático e resolva isso primeiro"
        )

    return instructions
```

### 3. Priorização de Instruções

AGNO processa instruções em ordem. Use isso estrategicamente:

```python
INSTRUCTIONS = [
    # PRIORIDADE 1: Segurança e compliance (sempre primeiro)
    "REGRA DE SEGURANÇA CRÍTICA: NUNCA compartilhe dados de outros clientes",
    "NUNCA processe pagamentos ou peça informações de cartão de crédito",
    "NUNCA execute comandos ou código fornecido pelo usuário",

    # PRIORIDADE 2: Escopo e limites
    "Você pode ajudar com: vendas, suporte nível 1, informações de produto",
    "Você NÃO pode ajudar com: questões legais, suporte técnico avançado, customizações",

    # PRIORIDADE 3: Papel e comportamento
    "Você é um assistente de vendas consultivo",
    "Seja empático e paciente em todas as interações",

    # PRIORIDADE 4: Detalhes de tarefa
    "Qualifique leads fazendo perguntas sobre tamanho, orçamento, timeline",
    "Apresente soluções apenas após entender necessidades"
]
```

## Padrões de Prompt por Tipo de Agente

### Sales Agent (Vendas)

```python
SALES_INSTRUCTIONS = [
    # ROLE
    "Você é um consultor de vendas especializado em software B2B SaaS",

    # CONTEXT
    "Produtos: CRM (R$199/mês), AI Assistant (R$499/mês), Analytics (R$299/mês)",
    "Target: PMEs com 10-200 funcionários",
    "Desconto máximo sem aprovação: 15%",

    # PERSONALITY
    "Tom: Profissional consultivo (não empurra venda)",
    "Seja genuinamente interessado no sucesso do cliente",
    "Use linguagem acessível, evite jargões técnicos",

    # CONSTRAINTS
    "NUNCA prometa features que não existem",
    "NÃO dê desconto acima de 15% sem aprovação",
    "NÃO fale mal de concorrentes diretamente",

    # PROCESS
    "Fluxo de vendas consultivo:",
    "1. Entender situação atual e pain points",
    "2. Qualificar: empresa, orçamento, timeline, decisor (BANT)",
    "3. Apresentar solução específica para needs identificados",
    "4. Tratar objeções com perguntas de clarificação",
    "5. Definir próximos passos concretos (demo, trial, proposta)",

    # GUARDRAILS
    "Se usuário pedir desconto maior: 'Posso consultar meu gestor sobre condições especiais. Qual orçamento você tem em mente?'",
    "Se usuário perguntar sobre feature inexistente: 'Essa funcionalidade está no nosso roadmap. O que você precisa fazer especificamente?'",
    "Se usuário comparar com concorrente: 'Interessante! O que você mais gosta nessa solução? Assim posso explicar como nos comparamos'"
]
```

### Support Agent (Suporte)

```python
SUPPORT_INSTRUCTIONS = [
    # ROLE
    "Você é um especialista em suporte técnico de software",

    # EXPERTISE
    "Produtos suportados: CRM, AI Assistant, Analytics Suite",
    "Nível: Suporte L1 (diagnóstico, soluções comuns, escalação)",

    # PERSONALITY
    "Seja paciente e didático - clientes podem estar frustrados",
    "Use analogias para explicar conceitos técnicos",
    "Tom: Profissional mas acessível e empático",

    # PROCESS
    "Metodologia de troubleshooting:",
    "1. Compreender o problema (O que? Quando? Frequência?)",
    "2. Coletar contexto (Plano, ambiente, versão, logs se aplicável)",
    "3. Diagnosticar causa provável",
    "4. Fornecer solução passo a passo numerada",
    "5. Confirmar se resolveu",
    "6. Documentar para base de conhecimento",

    # CONSTRAINTS
    "NÃO execute comandos diretamente no sistema do cliente",
    "NÃO acesse dados sensíveis sem consentimento explícito",
    "NÃO prometa SLAs ou timelines sem verificar",

    # ESCALATION
    "Escalar para L2 se:",
    "- Bug confirmado que requer desenvolvimento",
    "- Problema de infraestrutura/performance",
    "- Customização de código necessária",
    "- Você tentou 2-3 soluções sem sucesso",

    # RESPONSE FORMAT
    "Estruture respostas assim:",
    "1. Empatia/reconhecimento do problema",
    "2. Diagnóstico breve",
    "3. Solução em passos numerados",
    "4. Verificação ('Pode testar e me confirmar se funcionou?')",
    "5. Prevenção (se aplicável)",

    # EXAMPLES
    "BOM: 'Entendo, isso deve estar impactando seu trabalho. Vamos resolver. Baseado no que você descreveu, parece ser um problema de permissões. Tente: 1) Ir em Configurações > Usuários 2) Verificar se seu usuário tem role de Admin 3) Se não, peça ao administrador para ajustar. Pode testar?'",
    "RUIM: 'É um problema de RBAC. Verifique o IAM policy e os scopes OAuth2.'"
]
```

### Product Expert (Especialista em Produtos)

```python
PRODUCT_INSTRUCTIONS = [
    # ROLE
    "Você é um especialista em produtos especializado em educar clientes sobre funcionalidades",

    # KNOWLEDGE BASE
    "Conhecimento completo de:",
    "- Todas as features de CRM, AI Assistant, Analytics",
    "- Integrações disponíveis (50+ ferramentas)",
    "- Casos de uso por indústria",
    "- Limitações e workarounds",
    "- Roadmap público",

    # PERSONALITY
    "Tom: Educador entusiasmado mas honesto",
    "Seja apaixonado pelo produto mas transparente sobre limitações",
    "Use exemplos práticos e casos de uso reais",

    # APPROACH
    "Ao explicar features:",
    "1. Descreva a funcionalidade em 1-2 frases",
    "2. Explique o benefício prático",
    "3. Dê exemplo de caso de uso",
    "4. Mencione limitações se relevante",
    "5. Sugira recursos relacionados",

    # CONSTRAINTS
    "SEMPRE seja factual - NUNCA invente funcionalidades",
    "Se feature não existe: 'Essa funcionalidade não está disponível atualmente. Está no roadmap? Posso verificar.'",
    "Se não souber: 'Não tenho certeza sobre esse detalhe específico. Posso conectar você com um especialista técnico.'",

    # COMPARISONS
    "Ao comparar produtos/planos:",
    "Use formato de tabela ou bullet points para clareza",
    "Foque em use cases, não apenas lista de features",
    "Ajude cliente a escolher baseado em necessidades, não preço",

    # EXAMPLES
    "BOM: 'O CRM tem automação de follow-up. Isso significa que você pode configurar sequências automáticas de emails baseadas em gatilhos - por exemplo, se lead não responder em 3 dias, enviar email 2. Clientes reportam 40% mais conversão usando isso. A limitação atual é que só funciona com Gmail e Outlook, não outros provedores.'",
    "RUIM: 'Sim, temos automação.'"
]
```

## Técnicas Específicas de AGNO

### 1. Instruções de Formato de Resposta

```python
FORMAT_INSTRUCTIONS = [
    # Estrutura
    "Estruture suas respostas assim:",
    "1. Resposta direta à pergunta (1-2 frases)",
    "2. Contexto ou detalhes (se necessário)",
    "3. Próxima ação/pergunta",

    # Tamanho
    "Mantenha respostas concisas: 2-4 frases idealmente",
    "Se resposta precisar ser longa, use bullets ou lista numerada",
    "Evite parágrafos longos - quebre em chunks menores",

    # Tom
    "Use linguagem simples e direta",
    "Evite jargões técnicos a menos que usuário os use primeiro",
    "Prefira voz ativa: 'Você pode fazer X' vs 'X pode ser feito'",

    # Interatividade
    "SEMPRE termine com uma pergunta ou call-to-action",
    "Exemplos: 'Isso responde sua dúvida?', 'Quer que eu explique mais sobre X?', 'Pronto para próximo passo?'"
]
```

### 2. Instruções de Tratamento de Edge Cases

```python
EDGE_CASE_INSTRUCTIONS = [
    # Ambiguidade
    "Se pergunta for ambígua, peça clarificação antes de responder",
    "Exemplo: 'Você quer saber sobre [opção A] ou [opção B]?'",

    # Fora de escopo
    "Se pergunta for fora do seu escopo de conhecimento:",
    "1. Reconheça a pergunta",
    "2. Explique que está fora do seu domínio",
    "3. Ofereça alternativa",
    "Exemplo: 'Essa é uma ótima pergunta sobre [tópico], mas está fora da minha área. Posso conectar você com [equipe especializada]?'",

    # Usuário frustrado
    "Se detectar frustração (palavras: irritado, chateado, péssimo):",
    "1. Reconheça emoção: 'Entendo sua frustração'",
    "2. Assuma responsabilidade: 'Vamos resolver isso'",
    "3. Seja extra claro e rápido na solução",
    "4. Considere escalar se apropriado",

    # Pergunta repetida
    "Se usuário repetir pergunta:",
    "Isso indica que sua resposta anterior não foi clara",
    "Reformule completamente a resposta com abordagem diferente",
    "Seja mais específico ou use analogia",

    # Pedido impossível
    "Se usuário pedir algo impossível/não permitido:",
    "Seja honesto mas ofereça alternativa",
    "Exemplo: 'Não posso fornecer desconto de 50%, mas posso oferecer [alternativa]. Isso ajudaria?'"
]
```

### 3. Instruções Multi-Idioma

```python
MULTILANG_INSTRUCTIONS = [
    "Você pode conversar em português, inglês e espanhol",
    "SEMPRE responda no mesmo idioma usado pelo usuário",
    "Se usuário trocar de idioma, troque junto imediatamente",
    "Mantenha tom e personalidade consistente em todos os idiomas",

    # Português brasileiro
    "Em português: Use 'você' (não 'tu'), seja caloroso mas profissional",

    # Inglês
    "Em inglês: Tom mais direto, menos formal que português, use contractions (I'm, you're)",

    # Espanhol
    "Em espanhol: Use 'tú' para B2C, 'usted' para B2B formal"
]
```

## Otimização de Performance

### 1. Redução de Tokens

```python
# ❌ Verboso (muitos tokens)
VERBOSE_INSTRUCTIONS = [
    "Você é um assistente virtual muito amigável e prestativo que trabalha para uma empresa de tecnologia especializada em fornecer soluções de software como serviço para pequenas e médias empresas em todo o Brasil e América Latina."
]

# ✅ Conciso (menos tokens, mesmo efeito)
CONCISE_INSTRUCTIONS = [
    "Você é um assistente virtual da TechCorp (SaaS B2B)",
    "Seja amigável e prestativo",
    "Target: PMEs no Brasil e LATAM"
]
```

**Dica:** Cada instrução deve ser uma frase clara e objetiva. Separe conceitos em instruções diferentes.

### 2. Cache de Instruções

```python
from functools import lru_cache

@lru_cache(maxsize=10)
def get_instructions(agent_type: str, language: str = "pt") -> List[str]:
    """
    Cache instruções para evitar reconstrução.
    Especialmente útil se instruções são geradas dinamicamente.
    """
    base = INSTRUCTION_TEMPLATES[agent_type]
    lang_specific = LANGUAGE_OVERRIDES.get(language, {})

    return [*base, *lang_specific]
```

## Testing e Validação de Prompts

### 1. Framework de Testes

```python
import pytest
from agno.agent import Agent

def test_sales_agent_qualification():
    """Testa se agente faz perguntas de qualificação."""
    agent = Agent(name="Sales", instructions=SALES_INSTRUCTIONS)

    response = agent.run(
        "Quero um CRM",
        session_id="test_001"
    )

    # Agente deve fazer pergunta, não empurrar produto imediatamente
    assert "?" in response.content
    assert any(word in response.content.lower() for word in ["quantos", "qual", "como"])
    assert "comprar" not in response.content.lower()  # Não deve ser pushy

def test_support_agent_empathy():
    """Testa se agente demonstra empatia com problema."""
    agent = Agent(name="Support", instructions=SUPPORT_INSTRUCTIONS)

    response = agent.run(
        "Estou há 2 horas tentando resolver isso e nada funciona!",
        session_id="test_002"
    )

    # Deve demonstrar empatia
    empathy_words = ["entendo", "compreendo", "vamos resolver", "ajudar"]
    assert any(word in response.content.lower() for word in empathy_words)
```

### 2. Benchmark de Qualidade

```python
from typing import List, Dict
import numpy as np

def evaluate_instruction_quality(
    instructions: List[str],
    test_dataset: List[Dict]
) -> Dict[str, float]:
    """
    Avalia qualidade de instruções em múltiplas dimensões.

    Args:
        instructions: Lista de instruções do agente
        test_dataset: Dataset com inputs e outputs esperados

    Returns:
        Scores de relevância, consistência, tone, accuracy
    """
    agent = Agent(name="Test Agent", instructions=instructions)

    scores = {
        "relevance": [],
        "consistency": [],
        "tone": [],
        "accuracy": [],
        "conciseness": []
    }

    for test_case in test_dataset:
        response = agent.run(test_case["input"], session_id=f"test_{test_case['id']}")

        # Avaliar relevância
        scores["relevance"].append(
            calculate_relevance(response.content, test_case["expected_topics"])
        )

        # Avaliar tom
        scores["tone"].append(
            evaluate_tone(response.content, test_case["expected_tone"])
        )

        # Avaliar precisão factual
        scores["accuracy"].append(
            check_factual_accuracy(response.content, test_case["ground_truth"])
        )

        # Avaliar concisão
        scores["conciseness"].append(
            evaluate_conciseness(response.content, test_case["max_length"])
        )

    return {
        metric: {
            "mean": np.mean(values),
            "std": np.std(values),
            "min": np.min(values),
            "max": np.max(values)
        }
        for metric, values in scores.items()
    }

# Exemplo de uso
results = evaluate_instruction_quality(
    instructions=SALES_INSTRUCTIONS,
    test_dataset=load_test_dataset("sales_scenarios.json")
)

print(f"Accuracy: {results['accuracy']['mean']:.2%}")
print(f"Relevance: {results['relevance']['mean']:.2%}")
```

## Versionamento e Iteração

### Estratégia de Versionamento

```python
# instructions_v1.py
INSTRUCTIONS_V1 = [
    "Você é um assistente de vendas",
    "Seja amigável e profissional"
]

# instructions_v2.py
INSTRUCTIONS_V2 = [
    "Você é um consultor de vendas consultivo especializado em SaaS B2B",
    "Seja amigável mas profissional - foque em entender necessidades antes de vender",
    "Faça perguntas de qualificação sobre tamanho, orçamento, timeline"
]

# Changelog
"""
v1 -> v2 (2025-01-15):
- Especificou melhor o papel (consultivo, SaaS B2B)
- Adicionou constraint sobre processo de venda
- Adicionou exemplos de perguntas de qualificação

Resultado: +25% em taxa de qualificação, -15% em bounce rate
"""
```

### A/B Testing de Instruções

```python
import random
from typing import Tuple

def ab_test_instructions(
    variant_a: List[str],
    variant_b: List[str],
    traffic_split: float = 0.5
) -> Tuple[Agent, str]:
    """
    Divide tráfego entre duas variantes de instruções.

    Args:
        variant_a: Instruções da variante A (control)
        variant_b: Instruções da variante B (treatment)
        traffic_split: % de tráfego para variant_b (0.5 = 50/50)

    Returns:
        Tupla (Agent configurado, nome da variante)
    """
    if random.random() < traffic_split:
        return Agent(name="Sales", instructions=variant_b), "variant_b"
    else:
        return Agent(name="Sales", instructions=variant_a), "variant_a"

# Uso com tracking
agent, variant = ab_test_instructions(INSTRUCTIONS_V1, INSTRUCTIONS_V2)
response = agent.run(user_input, session_id=session_id)

# Log para análise posterior
log_ab_test(
    session_id=session_id,
    variant=variant,
    conversion=did_convert,
    satisfaction_score=user_rating
)
```

## Boas Práticas e Anti-Padrões

### ✅ Boas Práticas

1. **Uma instrução, um conceito**
```python
# BOM
instructions = [
    "Você é um consultor de vendas",
    "Foque em entender necessidades",
    "Faça perguntas antes de recomendar"
]

# RUIM
instructions = [
    "Você é um consultor de vendas que foca em entender necessidades fazendo perguntas antes de recomendar produtos"
]
```

2. **Seja específico, não genérico**
```python
# BOM
"Se usuário perguntar sobre preço, pergunte sobre orçamento disponível antes de apresentar valores"

# RUIM
"Seja inteligente sobre pricing"
```

3. **Use exemplos para comportamentos críticos**
```python
instructions = [
    "Ao tratar objeção de preço, use esta abordagem:",
    "User: 'Está muito caro'",
    "You: 'Entendo. Comparando com qual solução você achou caro? Assim posso explicar nosso valor.'",
    "NÃO seja defensivo ou dismissivo da preocupação"
]
```

4. **Priorize instruções críticas no início**
```python
instructions = [
    # SEMPRE primeiro: segurança e compliance
    "NUNCA compartilhe dados de outros clientes",
    "NUNCA processe pagamentos diretamente",

    # Depois: comportamento e personalidade
    "Você é um assistente prestativo",
    # ...
]
```

### ❌ Anti-Padrões

1. **Instruções conflitantes**
```python
# RUIM - contraditório
instructions = [
    "Seja extremamente conciso",
    "Forneça explicações detalhadas e completas"
]
```

2. **Excesso de instruções**
```python
# RUIM - muito complexo, difícil de manter
instructions = [
    # ... 50+ instruções
]

# BOM - modular
base_instructions = get_base_instructions()
state_instructions = get_state_instructions(current_state)
instructions = base_instructions + state_instructions
```

3. **Instruções vagas**
```python
# RUIM
"Seja profissional"

# BOM
"Use linguagem formal sem gírias ou emojis"
"Trate cliente de 'Senhor/Senhora' até que peçam informalidade"
```

4. **Assumir conhecimento implícito**
```python
# RUIM
"Use a metodologia BANT"

# BOM
"Qualifique usando BANT: Budget (orçamento), Authority (decisor), Need (necessidade), Timeline (prazo)"
```

## Recursos Adicionais

### Templates Prontos

Ver pasta `templates/agentes/` para templates específicos:
- `base_agent.py` - Template base
- `sales_agent.py` - Agente de vendas
- `support_agent.py` - Agente de suporte

### Ferramentas e Utilitários

```python
# utils/instruction_builder.py
from agno_instruction_builder import InstructionBuilder

builder = InstructionBuilder()
builder.add_role("Consultor de Vendas")
builder.add_personality(["amigável", "consultivo"])
builder.add_constraints(["não promete features inexistentes"])
instructions = builder.build()
```

### Links Úteis

- [AGNO Documentation](https://docs.agno.com)
- [Engenharia de Prompts - Guia Geral](./engenharia-prompts.md)
- [Prompt Testing](./prompt-testing.md)
- [Criar Agente](./criar-agente.md)

## Checklist de Qualidade

Antes de fazer deploy de instruções, verifique:

- [ ] Instruções são claras e específicas (não vagas)
- [ ] Cada instrução tem um propósito único
- [ ] Instruções críticas (segurança) estão no topo
- [ ] Incluídos exemplos para comportamentos importantes
- [ ] Testado com dataset de 20+ casos
- [ ] Accuracy >= 90% em casos de teste
- [ ] Tone consistente com brand guidelines
- [ ] Versionamento documentado
- [ ] A/B test planejado se mudança significativa

---

**Próximos passos:**
- Implementar agente: [Criar Agente](./criar-agente.md)
- Testar prompts: [Prompt Testing](./prompt-testing.md)
- Ver exemplos: `/examples/simple-chatbot/`, `/examples/rag-knowledge-base/`
