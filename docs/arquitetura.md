# Arquitetura do Framework

**Versão:** 1.0
**Data:** 2024-01-15
**Status:** Ativo

---

## 1. Visão Geral

Este framework fornece uma arquitetura completa e metodologia padronizada para desenvolvimento de **Agentes de IA para Atendimento Comercial**, com foco em escalabilidade, manutenibilidade e qualidade.

### 1.1 Objetivos Arquiteturais

- **Modularidade:** Componentes desacoplados e reutilizáveis
- **Escalabilidade:** Horizontal scaling sem mudanças arquiteturais
- **Manutenibilidade:** Código limpo, testável e bem documentado
- **Confiabilidade:** Tratamento robusto de erros e fallbacks
- **Observabilidade:** Logs, métricas e traces completos

---

## 2. Arquitetura Geral

### 2.1 Diagrama de Alto Nível

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                        │
│          (Web Chat, WhatsApp, Email, API, etc)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      API GATEWAY                             │
│  - Authentication                                            │
│  - Rate Limiting                                             │
│  - Load Balancing                                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   AGENT ORCHESTRATION                        │
│                                                              │
│  ┌────────────┐     ┌──────────────┐     ┌──────────────┐  │
│  │   Router   │────▶│Sales Agent   │     │Support Agent │  │
│  │   Agent    │     └──────────────┘     └──────────────┘  │
│  └────────────┘     ┌──────────────┐     ┌──────────────┐  │
│                     │Product Agent │     │ Custom Agent │  │
│                     └──────────────┘     └──────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│     LLM      │ │   MEMORY     │ │  KNOWLEDGE   │
│  (OpenAI,    │ │  (Redis +    │ │    BASE      │
│   Claude)    │ │ PostgreSQL)  │ │  (RAG/Docs)  │
└──────────────┘ └──────────────┘ └──────────────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     INTEGRATIONS                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   CRM    │  │  Email   │  │ Calendar │  │Analytics │   │
│  │(Salesf.) │  │(SendGrid)│  │ (Google) │  │(Mixpanel)│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
         │               │               │               │
         └───────────────┴───────────────┴───────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 OBSERVABILITY LAYER                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Logs   │  │ Metrics  │  │  Traces  │  │  Alerts  │   │
│  │(Struct.) │  │(Prometh.)│  │  (OTEL)  │  │(Alertmgr)│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Camadas da Arquitetura

### 3.1 Presentation Layer

**Responsabilidade:** Interface com usuários e sistemas externos

**Componentes:**
- API REST/GraphQL
- WebSocket para real-time chat
- Webhooks para integrações (WhatsApp, etc)
- SDK/Client libraries

**Tecnologias:**
- FastAPI (API framework)
- Uvicorn (ASGI server)
- Pydantic (validação)

### 3.2 Application Layer

**Responsabilidade:** Lógica de negócio e orquestração de agentes

**Componentes:**

**BaseAgent (Classe Abstrata):**
```python
BaseAgent
├── _load_prompts()         # Carrega prompts
├── _initialize_tools()     # Inicializa ferramentas
├── process()               # Processa input
├── validate_input()        # Validação
├── apply_guardrails()      # Guardrails
└── log_interaction()       # Logging
```

**Specialized Agents:**
- **Router Agent:** Identifica intenção e roteia
- **Sales Agent:** Qualificação e vendas
- **Support Agent:** Suporte técnico
- **Product Agent:** Informações de produto

**Padrões:**
- Template Method (BaseAgent)
- Strategy (diferentes LLMs)
- Chain of Responsibility (guardrails)
- Observer (logging/monitoring)

### 3.3 Domain Layer

**Responsabilidade:** Modelos e regras de negócio

**Entidades:**
```python
# Conversa
class Conversation:
    id: str
    user_id: str
    agent_id: str
    messages: List[Message]
    metadata: dict
    created_at: datetime

# Lead
class Lead:
    id: str
    name: str
    email: str
    score: int  # 0-100
    qualification: BANTQualification
    source: str

# Interação
class Interaction:
    user_input: str
    agent_response: str
    timestamp: datetime
    metadata: dict
```

### 3.4 Infrastructure Layer

**Responsabilidade:** Acesso a recursos externos

**Componentes:**

**LLM Clients:**
- OpenAI Client
- Anthropic Client
- Google AI Client
- Adapter pattern para abstração

**Memory:**
- **Short-term:** Redis (conversação ativa)
- **Long-term:** PostgreSQL (histórico)
- **Vector Store:** ChromaDB/Pinecone (RAG)

**Integrations:**
- CRM Client (Salesforce, HubSpot)
- Email Service (SendGrid)
- Calendar (Google Calendar)
- Analytics (Mixpanel)

---

## 4. Padrões de Design

### 4.1 Single-Agent vs Multi-Agent

**Single Agent:**
```
User → Agent → LLM → Response
```

**Quando usar:**
- Projetos simples (1-3 casos de uso)
- MVP rápido
- Time pequeno

**Multi-Agent:**
```
User → Router Agent → [Sales Agent]
                   → [Support Agent]
                   → [Product Agent]
```

**Quando usar:**
- Múltiplos domínios de conhecimento
- Necessidade de especialização
- Escalabilidade futura

### 4.2 Router Pattern

```python
class RouterAgent(BaseAgent):
    """Roteia para agente especializado."""

    def process(self, user_input, context):
        # 1. Identificar intenção
        intent = self.classify_intent(user_input)

        # 2. Selecionar agente
        agent = self.agents.get(intent.agent_type)

        # 3. Delegar
        return agent.process(user_input, context)
```

**Estratégias de roteamento:**
- **Baseado em keywords:** Simples, rápido
- **Classificação com LLM:** Mais preciso
- **ML Classifier:** Mais eficiente (custo)

### 4.3 RAG (Retrieval-Augmented Generation)

```
User Query
    │
    ▼
┌──────────────────┐
│ Embed Query      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Vector Search    │
│ (Top-k docs)     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ LLM + Context    │
│ Generate Answer  │
└────────┬─────────┘
         │
         ▼
     Response
```

**Quando usar RAG:**
- Base de conhecimento grande (>100 docs)
- Informações atualizadas frequentemente
- Necessidade de citações/fontes

### 4.4 Guardrails Pattern

```python
def apply_guardrails(response, context):
    checks = [
        check_sensitive_info,
        check_policy_compliance,
        check_hallucination,
        check_toxicity,
    ]

    for check in checks:
        passed, filtered = check(response, context)
        if not passed:
            return fallback_response()

    return response
```

---

## 5. Fluxo de Dados

### 5.1 Fluxo de Requisição

```
1. User sends message
   │
   ▼
2. API Gateway
   ├─ Authenticate
   ├─ Rate limit check
   └─ Route to service
   │
   ▼
3. Agent Orchestration
   ├─ Validate input
   ├─ Check prompt injection
   ├─ Load conversation context
   └─ Select agent
   │
   ▼
4. Agent Processing
   ├─ Build prompt with context
   ├─ Call LLM
   ├─ Execute tools if needed
   └─ Apply guardrails
   │
   ▼
5. Store & Integrate
   ├─ Update memory
   ├─ Create lead if qualified
   ├─ Send to CRM
   └─ Log interaction
   │
   ▼
6. Return Response
   └─ Format & send to user
```

### 5.2 Fluxo de Integração (CRM)

```python
# Com retry e fallback
@retry_with_backoff(max_retries=3)
def create_lead_in_crm(lead_data):
    try:
        # Tentar criar no CRM
        response = crm_client.create_lead(lead_data)
        return response

    except CRMUnavailable:
        # Fallback: armazenar em fila
        retry_queue.add(lead_data)
        # Retornar ID temporário
        return {"id": generate_temp_id(), "status": "queued"}
```

---

## 6. Decisões Arquiteturais (ADRs)

### ADR-001: Usar FastAPI como Framework Web

**Status:** Aceito
**Data:** 2024-01-01

**Contexto:**
Necessidade de API rápida com validação automática e docs.

**Decisão:**
Usar FastAPI.

**Consequências:**
✅ Performance alta (async)
✅ Validação automática (Pydantic)
✅ Docs geradas automaticamente
✅ Type hints nativos
❌ Curva de aprendizado (async)

---

### ADR-002: Redis para Memória de Curto Prazo

**Status:** Aceito
**Data:** 2024-01-05

**Contexto:**
Necessidade de cache rápido para conversações ativas.

**Decisão:**
Usar Redis com TTL de 30 minutos.

**Consequências:**
✅ Latência baixíssima (<1ms)
✅ TTL automático
✅ Suporte a estruturas complexas
❌ Custo adicional de infraestrutura
❌ Requer persistência em PostgreSQL

---

### ADR-003: Multi-Agent Architecture

**Status:** Aceito
**Data:** 2024-01-10

**Contexto:**
Necessidade de especialização e escalabilidade.

**Decisão:**
Arquitetura multi-agente com router.

**Consequências:**
✅ Especialização por domínio
✅ Escalabilidade (adicionar agentes)
✅ Manutenção mais fácil
❌ Complexidade maior
❌ Overhead de roteamento

---

## 7. Segurança

### 7.1 Camadas de Segurança

**Nível 1: API Gateway**
- API Key authentication
- Rate limiting (100 req/min)
- IP whitelist (se B2B)
- TLS 1.2+ obrigatório

**Nível 2: Input Validation**
- Max length enforcement
- Prompt injection detection
- XSS/SQL injection prevention
- Content filtering

**Nível 3: Output Validation**
- PII redaction
- Sensitive data detection
- Policy compliance
- Hallucination detection

**Nível 4: Data Protection**
- Encryption at rest
- Encryption in transit
- Audit logging
- LGPD compliance

### 7.2 Threat Model

| Ameaça | Mitigação |
|--------|-----------|
| Prompt Injection | Detecção de padrões + guardrails |
| DDoS | Rate limiting + auto-scaling |
| Data leakage | Output validation + redaction |
| Unauthorized access | API Key + JWT |
| Man-in-the-middle | TLS obrigatório |

---

## 8. Performance e Escalabilidade

### 8.1 Metas de Performance

| Métrica | Target | P95 | P99 |
|---------|--------|-----|-----|
| Response Time | <1s | <2s | <3s |
| Throughput | 100 req/s | - | - |
| Concurrent Users | 200 | 500 | 1000 |
| Error Rate | <0.5% | <1% | <2% |

### 8.2 Estratégias de Escalabilidade

**Horizontal Scaling:**
- Stateless application (sem sessão local)
- Load balancer (Nginx/AWS ALB)
- Auto-scaling baseado em CPU/requests

**Caching:**
- Prompt caching (reduce LLM calls)
- Response caching (respostas comuns)
- Token caching (authentication)

**Database Optimization:**
- Connection pooling
- Read replicas
- Indexes apropriados
- Query optimization

---

## 9. Observabilidade

### 9.1 Três Pilares

**Logs:**
- Estruturados (JSON)
- Trace IDs
- Centralizados
- Retenção: 30 dias

**Métricas:**
- Request rate
- Response time
- Error rate
- Business metrics

**Traces:**
- Distributed tracing (OpenTelemetry)
- End-to-end visibility
- Performance bottlenecks

### 9.2 Dashboards

Ver: `templates/monitoramento/dashboards.json`

---

## 10. Deployment

### 10.1 Ambientes

```
Development → Test → Staging → Production
```

**Características:**
- **Dev:** Local, mock integrations
- **Test:** CI/CD, automated tests
- **Staging:** Prod-like, real integrations (sandbox)
- **Production:** Real users, real data

### 10.2 Estratégia de Deploy

**Canary Deployment:**
```
1. Deploy para 5% do tráfego
2. Monitorar por 2-4h
3. Aumentar para 25% se estável
4. Aumentar para 50%
5. Completar para 100%
6. Rollback automático se error rate > 5%
```

---

## 11. Disaster Recovery

### 11.1 Backup

**PostgreSQL:**
- Backup diário automático
- Retenção: 30 dias
- Point-in-time recovery

**Redis:**
- Snapshot a cada 15min
- Retenção: 7 dias
- Reconstrução a partir de PostgreSQL

### 11.2 Plano de Recuperação

**RTO (Recovery Time Objective):** 1 hora
**RPO (Recovery Point Objective):** 15 minutos

**Procedimento:**
1. Ativar instância de backup
2. Restaurar último snapshot do banco
3. Reprocessar fila de retry
4. Validar com smoke tests
5. Comunicar usuários

---

## 12. Evolução da Arquitetura

### 12.1 Roadmap

**Fase 1 (Atual):**
- ✅ Single/Multi-agent básico
- ✅ Integrações core (CRM, email)
- ✅ Monitoring básico

**Fase 2 (Próximo):**
- RAG com vector store
- Multi-canal (WhatsApp, SMS)
- A/B testing de prompts

**Fase 3 (Futuro):**
- Fine-tuning de modelos
- Reinforcement learning
- Multi-idioma

### 12.2 Tech Debt

| Item | Prioridade | Estimativa |
|------|------------|------------|
| Implementar caching agressivo | Alta | 2 semanas |
| Migrar para gRPC (integrações) | Média | 3 semanas |
| Adicionar GraphQL API | Baixa | 4 semanas |

---

## Referências

- **Metodologia:** `/docs/metodologia/OVERVIEW.md`
- **Processos:** `/docs/processos/`
- **Guias:** `/docs/guias/`
- **Templates:** `/templates/`
- **Exemplos:** `/examples/`

---

**Última Atualização:** 2024-01-15
**Próxima Revisão:** 2024-04-15
**Owner:** Tech Lead
