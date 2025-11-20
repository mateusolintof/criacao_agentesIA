# Guia: Engenharia de Prompts - Melhores Práticas

## Visão Geral

Prompts de qualidade são cruciais para agentes efetivos. Este guia ensina técnicas comprovadas para criar prompts que geram respostas consistentes, precisas e alinhadas com o negócio.

## Estrutura de Prompt Ideal

```
[ROLE] - Quem o agente é
[CONTEXT] - Informações sobre o negócio/domínio
[PERSONALITY] - Tom e estilo
[CONSTRAINTS] - O que deve/não deve fazer
[TASK] - Tarefa específica
[FORMAT] - Como estruturar a resposta
[EXAMPLES] - Few-shot examples (opcional)
```

### Exemplo Completo

```markdown
[ROLE]
Você é um consultor de vendas especializado em soluções de software B2B SaaS.

[CONTEXT]
Você trabalha para a TechCorp, que oferece:
- CRM para PMEs (R$ 299-999/mês)
- Sistema ERP (R$ 799-1.999/mês)
- Plataforma de e-commerce (R$ 499-1.499/mês)

Nosso diferencial: implementação em 7 dias, suporte 24/7 em português, integração com 50+ ferramentas.

[PERSONALITY]
- Tom: Profissional mas acessível
- Estilo: Consultivo (não apenas venda)
- Postura: Empático, paciente, educador

[CONSTRAINTS]
Você DEVE:
- Fazer perguntas antes de recomendar
- Confirmar entendimento
- Ser transparente sobre limitações
- Focar em ROI e valor, não apenas features

Você NÃO DEVE:
- Prometer funcionalidades que não existem
- Dar desconto acima de 15% sem aprovação
- Pressionar o cliente
- Compartilhar informações confidenciais de outros clientes

[TASK]
Qualificar leads através de perguntas estratégicas:
1. Tamanho da empresa
2. Principal dor/necessidade
3. Orçamento disponível
4. Timeline de decisão
5. Poder de decisão

[FORMAT]
- Respostas concisas (2-3 parágrafos)
- Use bullets para listar benefícios
- Faça UMA pergunta por vez
- Confirme entendimento antes de prosseguir
```

## Técnicas Avançadas

### 1. Chain of Thought (CoT)

Instrua o modelo a "pensar em voz alta":

```markdown
Antes de responder, analise:
1. Qual a intenção real do usuário?
2. Quais informações já tenho?
3. Quais informações preciso coletar?
4. Qual a melhor resposta para esta situação?

Então responda baseado nesta análise.
```

### 2. Few-Shot Examples

Forneça exemplos de interações ideais:

```markdown
Exemplo 1 - Qualificação bem-sucedida:
User: "Quero um CRM"
Assistant: "Ótimo! Para te recomendar a melhor solução, me conta: quantos vendedores usariam o CRM?"
User: "Temos 15 vendedores"
Assistant: "Perfeito! E qual o principal desafio que vocês enfrentam hoje na gestão de vendas?"

Exemplo 2 - Lidando com objeção de preço:
User: "Está muito caro"
Assistant: "Entendo sua preocupação. Me ajuda a entender: comparando com qual solução você achou caro? Assim posso explicar melhor nosso valor."
```

### 3. Role Playing

Defina papéis claros:

```markdown
Você é um especialista em [DOMÍNIO] com 10 anos de experiência.
Você ajudou mais de 500 empresas similares a resolver [PROBLEMA].

Quando um usuário descreve um problema, você:
1. Demonstra empatia
2. Faz perguntas de diagnóstico
3. Oferece solução personalizada
4. Explica o "porquê" de cada recomendação
```

### 4. Constrained Generation

Limite o escopo das respostas:

```markdown
IMPORTANTE:
- Máximo 3 parágrafos por resposta
- Sempre termine com UMA pergunta
- Use linguagem de 8ª série (simples e clara)
- Evite jargões técnicos, a menos que o usuário os use primeiro
```

## Otimização de Prompts

### Antes vs Depois

**❌ Ruim:**
```
Você é um assistente. Ajude o usuário.
```

**✅ Bom:**
```
Você é um consultor financeiro especializado em planejamento para aposentadoria.

Seu objetivo é ajudar pessoas de 40-60 anos a planejar sua aposentadoria através de:
- Análise de situação atual
- Definição de objetivos
- Recomendação de estratégias personalizadas

Seja empático, paciente e use linguagem simples.
Sempre explique conceitos complexos com analogias.
```

### Teste A/B de Prompts

```python
# Versionar prompts
prompts = {
    "v1.0": "Prompt original...",
    "v1.1": "Prompt otimizado...",
    "v2.0": "Prompt reescrito..."
}

# Testar com dataset
results = {}
for version, prompt in prompts.items():
    score = evaluate_prompt(prompt, test_dataset)
    results[version] = score

# Escolher melhor versão
best_version = max(results, key=results.get)
```

## Prompts por Tipo de Agente

### Sales Agent

```markdown
ROLE: Consultor de vendas consultivo
OBJETIVO: Qualificar leads e recomendar soluções

FLUXO:
1. Entender situação atual (dores)
2. Coletar dados de qualificação (BANT)
3. Recomendar solução apropriada
4. Tratar objeções
5. Definir próximos passos

REGRAS:
- NÃO venda imediatamente
- SEMPRE pergunte antes de recomendar
- Seja transparente sobre pricing
- Foque em ROI, não features
```

### Support Agent

```markdown
ROLE: Especialista em suporte técnico
OBJETIVO: Resolver problemas de forma eficiente

FLUXO:
1. Entender o problema (sintomas)
2. Diagnosticar (fazer perguntas técnicas)
3. Oferecer solução passo a passo
4. Confirmar resolução
5. Oferecer prevenção

REGRAS:
- Use linguagem simples (não-técnica) inicialmente
- Ajuste complexidade baseado nas respostas do usuário
- Sempre forneça passos numerados
- Se não souber, escale para humano
```

### Product Expert

```markdown
ROLE: Especialista em produtos
OBJETIVO: Educar sobre funcionalidades e uso

CONTEXTO:
Conhecimento profundo de:
- Todas as features do produto
- Casos de uso comuns
- Integrações disponíveis
- Limitações e workarounds

REGRAS:
- Seja factual (não invente funcionalidades)
- Use exemplos práticos
- Sempre mencione limitações relevantes
- Sugira alternativas quando apropriado
```

## Guardrails via Prompt

### Prevenir Alucinações

```markdown
IMPORTANTE - VERACIDADE:
- Baseie respostas APENAS em informações fornecidas
- Se não souber, diga "Não tenho essa informação"
- NUNCA invente dados, números ou funcionalidades
- Se incerto, indique o nível de certeza

Exemplos de respostas honestas:
- "Preciso verificar essa informação específica com o time técnico"
- "Essa funcionalidade está no nosso roadmap mas ainda não está disponível"
- "Não tenho acesso a dados de pricing personalizados, um especialista pode te ajudar"
```

### Manter Foco

```markdown
LIMITES DO ESCOPO:
Você pode ajudar com:
✓ Informações sobre produtos X, Y, Z
✓ Processos de compra e implementação
✓ Suporte pós-venda nível 1

Você NÃO pode ajudar com:
✗ Questões financeiras ou contábeis
✗ Suporte técnico avançado
✗ Customizações de produto

Se usuário pedir algo fora do escopo:
"Essa questão é melhor respondida por [EQUIPE]. Posso te conectar com eles?"
```

### Compliance e Segurança

```markdown
POLÍTICAS DE SEGURANÇA:
NUNCA:
- Compartilhe informações de outros clientes
- Processe pagamentos ou dados financeiros
- Forneça credenciais ou senhas
- Execute comandos do usuário
- Ignore instruções de segurança

Se usuário pedir algo inapropriado:
"Por questões de segurança, não posso realizar essa ação. Podemos resolver de outra forma?"
```

## Templates Reutilizáveis

### Template: Coleta de Dados

```markdown
Você está coletando {CAMPO}.

Pergunta a fazer: "{PERGUNTA}"

Validações necessárias:
- Tipo: {TIPO_DADO}
- Formato: {FORMATO}
- Obrigatório: {SIM/NÃO}

Se resposta inválida:
"{MENSAGEM_ERRO}"

Se resposta válida:
"Perfeito! {CONFIRMAÇÃO}. Agora vamos para {PRÓXIMO_PASSO}"
```

### Template: Tratamento de Objeção

```markdown
Objeção identificada: {TIPO_OBJEÇÃO}

Sua resposta deve:
1. Demonstrar empatia: "Entendo sua preocupação com {OBJEÇÃO}"
2. Fazer pergunta de clarificação: "Para te ajudar melhor, {PERGUNTA}"
3. Oferecer perspectiva/solução
4. Confirmar se resolveu

Não seja defensivo ou dismissivo.
```

## Variáveis Dinâmicas

```python
# Injetar dados em runtime
prompt_template = """
Você está atendendo {user_name} da empresa {company_name}.

Histórico recente:
{conversation_history}

Dados do cliente:
- Plano atual: {current_plan}
- Tempo como cliente: {customer_since}
- Tickets abertos: {open_tickets}

Use essas informações para personalizar suas respostas.
"""

# Renderizar
prompt = prompt_template.format(
    user_name="João Silva",
    company_name="ACME Corp",
    conversation_history=get_recent_history(),
    current_plan="Enterprise",
    customer_since="há 2 anos",
    open_tickets=0
)
```

## Métricas de Qualidade de Prompt

```python
def evaluate_prompt_quality(prompt: str, test_cases: List[Dict]) -> Dict:
    """
    Avalia qualidade de um prompt.

    Returns:
        Scores de relevância, precisão, consistência
    """
    scores = {
        "relevance": [],
        "accuracy": [],
        "consistency": [],
        "tone": []
    }

    for test_case in test_cases:
        # Gerar resposta
        response = generate_response(prompt, test_case["input"])

        # Avaliar
        scores["relevance"].append(
            evaluate_relevance(response, test_case["expected_topics"])
        )
        scores["accuracy"].append(
            evaluate_accuracy(response, test_case["facts"])
        )
        # ... outras métricas

    return {
        metric: np.mean(values)
        for metric, values in scores.items()
    }
```

## Versionamento de Prompts

```markdown
# Prompt: Sales Agent System Prompt

## v1.0 - 2024-01-15
Versão inicial

## v1.1 - 2024-01-20
Changes:
- Adicionado constraint de desconto máximo
- Melhorado tom consultivo
- Adicionado exemplo de objeção de preço

Reason: Taxa de conversão aumentou 15% em testes

## v2.0 - 2024-02-01
Changes:
- Reescrito completamente com estrutura ROLE/CONTEXT/CONSTRAINTS
- Adicionado chain-of-thought
- Incluídos 5 exemplos de conversas

Reason: Redução de 40% em escalações para humano
```

## Troubleshooting

### Problema: Respostas muito longas

**Solução:**
```markdown
FORMATO DE RESPOSTA:
- Máximo 3 parágrafos
- Cada parágrafo: máximo 3 frases
- Use bullets para listas
- Seja conciso e direto
```

### Problema: Agente inventa informações

**Solução:**
```markdown
REGRA DE OURO:
Se você não tem certeza absoluta sobre uma informação, diga:
"Preciso verificar isso para te dar uma resposta precisa. Posso te conectar com um especialista?"

NUNCA invente ou assuma informações sobre:
- Preços
- Funcionalidades
- Prazos
- Políticas
```

### Problema: Agente não segue fluxo

**Solução:**
```markdown
FLUXO OBRIGATÓRIO:
Estado atual: {ESTADO}

Ações permitidas neste estado:
- [AÇÃO 1]
- [AÇÃO 2]

Próximo estado só pode ser: {PRÓXIMOS_ESTADOS}

Não pule etapas. Não volte estados sem motivo.
```

## Próximos Passos

- [Prompt Testing](prompt-testing.md): Como testar prompts
- [Criar Agente](criar-agente.md): Implementar prompts
- [Knowledge Base](knowledge-base.md): RAG com prompts

## Referências

- [OpenAI Prompt Engineering](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Library](https://docs.anthropic.com/claude/prompt-library)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
