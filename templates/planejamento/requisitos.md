# Documento de Requisitos

**Projeto:** [NOME DO PROJETO]
**Cliente:** [NOME DO CLIENTE]
**Versão:** 1.0
**Data:** [DATA]
**Responsável:** [NOME]

---

## 1. Informações Gerais

### 1.1 Objetivo do Projeto
[Descrever em 2-3 parágrafos o objetivo principal do projeto e o problema que ele resolve]

**Exemplo:**
> Desenvolver um agente de IA para atendimento comercial que qualifique leads automaticamente 24/7, responda dúvidas sobre produtos e serviços, e agende demonstrações com o time de vendas. O objetivo é aumentar a taxa de conversão de leads e reduzir o tempo de resposta inicial de 24h para menos de 1 minuto.

### 1.2 Stakeholders

| Nome | Papel | Responsabilidade | Contato |
|------|-------|------------------|---------|
| [NOME] | Sponsor | Aprovações e budget | [EMAIL] |
| [NOME] | Product Owner | Requisitos e priorização | [EMAIL] |
| [NOME] | Tech Lead | Arquitetura e implementação | [EMAIL] |
| [NOME] | UX Designer | Experiência do usuário | [EMAIL] |
| [NOME] | QA Lead | Qualidade e testes | [EMAIL] |

### 1.3 Escopo Geral

**In Scope (O que será feito):**
- [ ] [ITEM 1]
- [ ] [ITEM 2]
- [ ] [ITEM 3]

**Out of Scope (O que NÃO será feito nesta fase):**
- [ ] [ITEM 1]
- [ ] [ITEM 2]

---

## 2. Requisitos Funcionais

### RF001: [Nome do Requisito]

**Prioridade:** ⬛ Crítico | ⬜ Alto | ⬜ Médio | ⬜ Baixo

**Descrição:**
[Descrever detalhadamente o requisito]

**Critérios de Aceitação:**
- [ ] Critério 1
- [ ] Critério 2
- [ ] Critério 3

**User Story:**
```
Como [TIPO DE USUÁRIO]
Eu quero [AÇÃO]
Para que [BENEFÍCIO/OBJETIVO]
```

**Cenários de Teste:**

**Cenário 1: Happy Path**
```gherkin
Given [condição inicial]
When [ação]
Then [resultado esperado]
```

**Cenário 2: Edge Case**
```gherkin
Given [condição]
When [ação]
Then [resultado]
```

**Dependências:**
- [DEPENDÊNCIA 1]
- [DEPENDÊNCIA 2]

**Estimativa:** [PONTOS/HORAS]

---

### RF002: Qualificação Automática de Leads

**Prioridade:** ⬛ Crítico

**Descrição:**
O agente deve ser capaz de conduzir uma conversa com o lead para coletar informações qualificadoras (BANT: Budget, Authority, Need, Timeline) e atribuir um score de qualificação de 0-100.

**Critérios de Aceitação:**
- [ ] Agente faz perguntas qualificadoras de forma natural na conversa
- [ ] Sistema calcula score baseado em: orçamento (30%), autoridade (25%), necessidade (25%), timeline (20%)
- [ ] Leads com score >= 70 são marcados como "qualificados"
- [ ] Leads com score < 40 são marcados como "baixa prioridade"
- [ ] Sistema captura: nome, email, empresa, cargo, necessidade, orçamento, timeline
- [ ] Dados são enviados para CRM automaticamente

**User Story:**
```
Como gerente de vendas
Eu quero que os leads sejam qualificados automaticamente
Para que meu time foque apenas em leads com alto potencial de conversão
```

**Cenários de Teste:**

**Cenário 1: Lead Qualificado**
```gherkin
Given um visitante acessa o chat
When ele informa orçamento > R$ 5000, é decisor, necessidade clara, timeline < 3 meses
Then o score deve ser >= 70
And o lead é marcado como "qualificado"
And uma notificação é enviada para o vendedor
```

**Cenário 2: Lead Desqualificado**
```gherkin
Given um visitante no chat
When ele não tem orçamento, não é decisor, necessidade vaga
Then o score deve ser < 40
And o lead é marcado como "baixa prioridade"
And nenhuma notificação urgente é enviada
```

**Cenário 3: Informações Parciais**
```gherkin
Given um visitante que responde parcialmente
When ele fornece 2 de 4 informações BANT
Then o score é calculado com os dados disponíveis
And o campo "completude" indica "parcial"
```

**Dependências:**
- Integração com CRM (RF005)
- Sistema de notificações (RF012)

**Estimativa:** 13 pontos

---

### RF003: [Outro Requisito]

[Repetir estrutura acima para cada requisito funcional]

---

## 3. Requisitos Não-Funcionais

### RNF001: Performance

**Categoria:** Performance

**Requisito:**
- Tempo de resposta p95 < 2 segundos
- Tempo de resposta p99 < 5 segundos
- Throughput: suportar 100 conversas simultâneas

**Medição:**
- Monitorar com Prometheus/Grafana
- Alertar se p95 > 3s por 5 minutos

**Prioridade:** ⬛ Crítico

---

### RNF002: Disponibilidade

**Categoria:** Reliability

**Requisito:**
- Uptime de 99.5% (aproximadamente 3.6 horas de downtime por mês)
- Sistema deve ter fallback para indisponibilidade de APIs externas
- Implementar circuit breaker para integrações

**Medição:**
- Monitorar uptime com health checks a cada 30s
- Alertar em caso de downtime > 1 minuto

**Prioridade:** ⬛ Crítico

---

### RNF003: Escalabilidade

**Categoria:** Scalability

**Requisito:**
- Sistema deve escalar horizontalmente (stateless)
- Suportar crescimento de 100 para 1000 conversas simultâneas sem mudanças arquiteturais
- Auto-scaling baseado em CPU (> 70%) e memória (> 80%)

**Medição:**
- Testes de carga com 500, 1000, 1500 usuários simultâneos
- Monitorar uso de recursos

**Prioridade:** ⬜ Alto

---

### RNF004: Segurança

**Categoria:** Security

**Requisito:**
- Comunicação HTTPS obrigatória (TLS 1.2+)
- Autenticação via API Key ou OAuth 2.0
- Rate limiting: 100 requisições por minuto por IP
- Input validation para prevenir injection attacks
- Logs não devem conter dados sensíveis (redaction)
- Compliance com LGPD (consentimento, right to deletion)

**Medição:**
- Security scan automatizado (OWASP Top 10)
- Penetration testing antes do deploy
- Auditoria de logs mensalmente

**Prioridade:** ⬛ Crítico

---

### RNF005: Observabilidade

**Categoria:** Monitoring

**Requisito:**
- Logs estruturados (JSON) com trace IDs
- Métricas: latência, throughput, error rate, token usage
- Distributed tracing para requests
- Dashboards: overview, performance, business metrics
- Alertas configurados para cenários críticos

**Medição:**
- Cobertura de logs: 100% de endpoints críticos
- Métricas coletadas a cada 15 segundos
- Alertas testados mensalmente

**Prioridade:** ⬜ Alto

---

### RNF006: Usabilidade

**Categoria:** Usability

**Requisito:**
- Tempo médio para agente responder primeira pergunta: < 5 segundos
- Taxa de compreensão de intenção: >= 90%
- Taxa de satisfação do usuário (CSAT): >= 4.0/5.0
- Conversa deve parecer natural (não robótica)

**Medição:**
- Coletar CSAT ao final de cada conversa
- Analisar intent accuracy semanalmente
- Revisar conversas com baixo CSAT

**Prioridade:** ⬜ Alto

---

### RNF007: Manutenibilidade

**Categoria:** Maintainability

**Requisito:**
- Código com cobertura de testes >= 80%
- Documentação atualizada (API, arquitetura, runbook)
- Prompts versionados e com changelog
- Deploy via CI/CD com rollback automático

**Medição:**
- Coverage report em cada PR
- Docs revisados a cada sprint
- Deploy sem downtime

**Prioridade:** ⬜ Médio

---

### RNF008: Custo

**Categoria:** Cost

**Requisito:**
- Custo por conversa < R$ 10
- Orçamento mensal total < R$ 15.000
- Otimizar uso de tokens (prompt caching, modelos menores)

**Medição:**
- Dashboard de custos atualizado diariamente
- Alerta se custo mensal projetado > R$ 15k
- Revisão mensal de otimizações

**Prioridade:** ⬜ Alto

---

## 4. Requisitos de Integração

### RI001: Integração com CRM Salesforce

**Sistema:** Salesforce Sales Cloud
**Tipo:** REST API
**Propósito:** Criar e atualizar leads

**Operações necessárias:**
- [ ] Criar lead (POST /leads)
- [ ] Atualizar lead (PATCH /leads/{id})
- [ ] Buscar lead por email (GET /leads?email={email})

**SLA:** Resposta < 3s, disponibilidade 99.9%

**Prioridade:** ⬛ Crítico

**Detalhes:** Ver `templates/integracao/template-spec-api.md`

---

### RI002: Integração com Sistema de Email

**Sistema:** SendGrid
**Tipo:** REST API
**Propósito:** Enviar emails transacionais e follow-ups

**Operações necessárias:**
- [ ] Enviar email individual
- [ ] Enviar email com template
- [ ] Rastrear abertura/cliques

**SLA:** Entrega < 1 minuto, taxa de entrega > 95%

**Prioridade:** ⬜ Alto

---

## 5. Requisitos de Dados

### RD001: Armazenamento de Conversas

**Descrição:** Armazenar histórico completo de conversas

**Estrutura:**
```json
{
  "conversation_id": "uuid",
  "user_id": "string",
  "agent_id": "string",
  "messages": [
    {
      "role": "user|assistant",
      "content": "string",
      "timestamp": "ISO-8601"
    }
  ],
  "metadata": {
    "channel": "web|whatsapp|email",
    "lead_score": "number",
    "tags": ["array"]
  },
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601"
}
```

**Retenção:** 2 anos, depois arquivar ou deletar (LGPD)

**Volume estimado:** 10.000 conversas/mês, 5 mensagens/conversa = 50k mensagens/mês

---

### RD002: Catálogo de Produtos

**Descrição:** Base de conhecimento sobre produtos e serviços

**Estrutura:**
```json
{
  "product_id": "string",
  "name": "string",
  "description": "string",
  "features": ["array"],
  "pricing": {...},
  "faq": [...]
}
```

**Atualização:** Manual, via API ou upload de arquivo

**Sincronização:** Verificar updates a cada 1 hora

---

## 6. Restrições e Suposições

### 6.1 Restrições

**Técnicas:**
- Deve usar AWS como cloud provider
- Backend deve ser Python 3.11+
- Banco de dados: PostgreSQL 14+ para dados estruturados, Redis para cache
- LLM: OpenAI GPT-4 ou Anthropic Claude

**Negócio:**
- Budget total do projeto: R$ 150.000
- Prazo: 12 semanas
- Equipe: 4 desenvolvedores, 1 designer, 1 QA

**Regulatórias:**
- Compliance com LGPD
- Não processar dados de saúde (HIPAA) nesta fase
- Dados devem ficar em território nacional (data residency)

### 6.2 Suposições

- Cliente já possui CRM Salesforce configurado
- Cliente fornecerá catálogo de produtos
- Volume inicial: 1.000 conversas/mês, crescendo 20% ao mês
- Idioma: apenas Português (Brasil) na v1
- Horário de pico: 9h-18h, seg-sex

---

## 7. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Qualidade das respostas do LLM abaixo do esperado | Média | Alto | Testar múltiplos prompts, usar RAG, ter fallback para humano |
| Custos de LLM acima do orçamento | Alta | Médio | Implementar caching agressivo, usar modelos menores onde possível |
| Integração com CRM complexa | Baixa | Alto | POC de integração na primeira semana |
| Taxa de adoção pelos usuários baixa | Média | Alto | Testes de usabilidade, iteração rápida |
| Latência alta em horário de pico | Média | Médio | Load testing, auto-scaling, CDN |

---

## 8. Critérios de Sucesso

**Métricas de Sucesso (após 3 meses em produção):**

| Métrica | Baseline | Meta |
|---------|----------|------|
| Taxa de conversão de leads | 12% | 18% |
| Tempo de primeira resposta | 24h | < 1min |
| CSAT (satisfação) | N/A | >= 4.0/5.0 |
| Volume de leads qualificados | 200/mês | 300/mês |
| Custo por lead qualificado | R$ 80 | R$ 50 |
| Taxa de adoção (% de visitantes que interagem) | N/A | >= 25% |

---

## 9. Entregáveis

### Fase 1: MVP (4 semanas)
- [ ] Agente básico de chat (texto)
- [ ] Qualificação de leads (BANT)
- [ ] Integração com CRM
- [ ] Dashboard de métricas básico

### Fase 2: Expansão (4 semanas)
- [ ] Integração com WhatsApp
- [ ] Base de conhecimento (RAG)
- [ ] Agendamento de demos
- [ ] Relatórios avançados

### Fase 3: Otimização (4 semanas)
- [ ] Multi-agente (routing)
- [ ] A/B testing de prompts
- [ ] Análise de sentimento
- [ ] Automações avançadas

---

## 10. Cronograma Macro

```
Semana 1-2:   Descoberta e Design
Semana 3-6:   Desenvolvimento MVP
Semana 7-8:   Testes e Ajustes
Semana 9:     Deploy Canary
Semana 10-12: Expansão e Otimização
```

---

## 11. Glossário

| Termo | Definição |
|-------|-----------|
| BANT | Budget, Authority, Need, Timeline - framework de qualificação |
| Lead | Potencial cliente que demonstrou interesse |
| CSAT | Customer Satisfaction Score |
| RAG | Retrieval-Augmented Generation |
| p95 | Percentil 95 (95% das requisições) |

---

## 12. Aprovações

| Stakeholder | Papel | Data | Assinatura |
|-------------|-------|------|------------|
| [NOME] | Sponsor | | |
| [NOME] | Product Owner | | |
| [NOME] | Tech Lead | | |

---

## 13. Histórico de Versões

| Versão | Data | Autor | Mudanças |
|--------|------|-------|----------|
| 1.0 | [DATA] | [NOME] | Versão inicial |
| | | | |

---

## Anexos

- [Anexo A: Wireframes]
- [Anexo B: Diagramas de Arquitetura]
- [Anexo C: Análise de Concorrentes]
