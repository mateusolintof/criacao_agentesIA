# Template de Prompt

## Informações do Prompt

- **Nome**: [NOME_DO_PROMPT]
- **Versão**: 1.0
- **Data**: [DATA]
- **Autor**: [NOME]
- **Agente**: [NOME_DO_AGENTE]
- **Objetivo**: [DESCREVER OBJETIVO]

## System Prompt

```
[ROLE]
Você é [PAPEL/FUNÇÃO]. [CONTEXTO ADICIONAL].

[CONTEXT]
Você trabalha para [EMPRESA/NEGÓCIO].
[INFORMAÇÕES SOBRE O NEGÓCIO, PRODUTOS, SERVIÇOS].

[PERSONALITY]
Tom de voz: [formal/casual/amigável/profissional]
Características: [empático, objetivo, consultivo, etc]
Postura: [proativa/reativa/consultiva]

[CONSTRAINTS]
Você DEVE:
- [REGRA 1]
- [REGRA 2]
- [REGRA 3]

Você NÃO DEVE:
- [RESTRIÇÃO 1]
- [RESTRIÇÃO 2]
- [RESTRIÇÃO 3]

[TASK]
Sua tarefa é: [DESCREVER TAREFA ESPECÍFICA]

[FORMAT]
Suas respostas devem:
- [FORMATO 1]
- [FORMATO 2]
- [FORMATO 3]
```

## Few-Shot Examples

### Exemplo 1: [CENÁRIO]

**User**:
```
[MENSAGEM DO USUÁRIO]
```

**Assistant**:
```
[RESPOSTA IDEAL]
```

**Explicação**: [POR QUE ESTA É UMA BOA RESPOSTA]

---

### Exemplo 2: [CENÁRIO]

**User**:
```
[MENSAGEM DO USUÁRIO]
```

**Assistant**:
```
[RESPOSTA IDEAL]
```

**Explicação**: [POR QUE ESTA É UMA BOA RESPOSTA]

---

### Exemplo 3: [CENÁRIO EDGE CASE]

**User**:
```
[MENSAGEM DO USUÁRIO]
```

**Assistant**:
```
[COMO LIDAR COM EDGE CASE]
```

**Explicação**: [POR QUE ESTE TRATAMENTO É ADEQUADO]

## Variáveis Dinâmicas

Liste variáveis que serão injetadas em runtime:

- `{user_name}`: Nome do usuário
- `{product_catalog}`: Catálogo de produtos relevantes
- `{user_history}`: Histórico de interações
- `{current_context}`: Contexto atual da conversa
- [ADICIONAR OUTRAS VARIÁVEIS]

## Validações

Após gerar resposta, validar:

- [ ] Resposta está no tom adequado
- [ ] Não contém informações sensíveis
- [ ] Segue restrições definidas
- [ ] Formato está correto
- [ ] Informações são precisas
- [ ] [ADICIONAR OUTRAS VALIDAÇÕES]

## Métricas de Sucesso

Como medir qualidade deste prompt:

- **Relevância**: [CRITÉRIO]
- **Precisão**: [CRITÉRIO]
- **Completude**: [CRITÉRIO]
- **Tom**: [CRITÉRIO]
- **Target Score**: [VALOR MÍNIMO]

## Casos de Teste

### Teste 1: Happy Path
**Input**: [INPUT]
**Expected Output**: [OUTPUT ESPERADO]

### Teste 2: Edge Case
**Input**: [INPUT]
**Expected Output**: [OUTPUT ESPERADO]

### Teste 3: Error Handling
**Input**: [INPUT PROBLEMÁTICO]
**Expected Output**: [COMO DEVE LIDAR]

## Notas de Implementação

- [NOTA 1 SOBRE IMPLEMENTAÇÃO]
- [NOTA 2 SOBRE IMPLEMENTAÇÃO]
- [CONSIDERAÇÕES ESPECIAIS]

## Histórico de Versões

### v1.0 - [DATA]
- Versão inicial
- [MUDANÇAS]

### v1.1 - [DATA]
- [MUDANÇAS]
- [MOTIVO]
