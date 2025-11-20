# Processo 5: Deploy e Monitoramento

## Objetivo

Realizar o deploy da solução em produção de forma segura, configurar monitoramento completo e garantir operação estável.

## Entradas

- Código aprovado
- Testes validados
- Aprovação formal do cliente
- Infraestrutura provisionada
- Documentação completa

## Atividades

### 5.1 Preparação para Deploy

**5.1.1 Verificação de Pré-requisitos**

- [ ] Infraestrutura provisionada
- [ ] Secrets configurados
- [ ] Integrações em produção testadas
- [ ] DNS configurado
- [ ] Certificados SSL válidos
- [ ] Backups configurados
- [ ] Monitoramento pronto
- [ ] Alertas configurados
- [ ] Documentação de operação pronta
- [ ] Time treinado

**5.1.2 Ambiente de Produção**

**Componentes**:
- **Application servers**: Executam agentes
- **API Gateway**: Controle de acesso e rate limiting
- **Load balancer**: Distribuição de carga
- **Database**: Armazenamento de conversas e dados
- **Vector database**: Knowledge base
- **Cache layer**: Redis/Memcached
- **Message queue**: Para processamento assíncrono
- **CDN**: Conteúdo estático

**5.1.3 Estratégia de Deploy**

Escolher estratégia adequada:

**Blue-Green Deployment**:
- Dois ambientes idênticos
- Deploy em "green"
- Swap quando validado
- Fácil rollback

**Canary Deployment**:
- Deploy gradual
- 5% → 25% → 50% → 100%
- Monitorar métricas
- Rollback se problemas

**Rolling Deployment**:
- Atualizar instâncias gradualmente
- Sempre mantém serviço disponível
- Mais lento que blue-green

**Recomendado para IA Agents**: Canary (permite validar com usuários reais gradualmente)

### 5.2 Execução do Deploy

**5.2.1 Checklist de Deploy**

**Pré-Deploy**:
- [ ] Backup completo
- [ ] Notificar stakeholders
- [ ] Comunicar manutenção (se aplicável)
- [ ] Validar ambiente de produção
- [ ] Configurar feature flags
- [ ] Preparar rollback plan

**Durante Deploy**:
- [ ] Executar migration de banco
- [ ] Deploy da aplicação
- [ ] Validar health checks
- [ ] Smoke tests
- [ ] Validar integrações
- [ ] Verificar logs

**Pós-Deploy**:
- [ ] Monitorar métricas
- [ ] Validar funcionalidades críticas
- [ ] Confirmar integrações funcionando
- [ ] Notificar conclusão
- [ ] Documentar deploy

**5.2.2 Deploy Gradual (Canary)**

**Fase 1: 5% de tráfego** (2-4 horas)
```bash
# Configurar weight no load balancer
kubectl set image deployment/agents \
  agents=agents:v2.0 \
  --record

kubectl scale deployment/agents-canary \
  --replicas=1

# Monitor metrics
```

**Validar**:
- Error rate < 1%
- Response time p95 < 2s
- No increase in errors
- User satisfaction maintained

**Fase 2: 25% de tráfego** (4-8 horas)
- Aumentar réplicas canary
- Continuar monitorando
- Validar métricas de negócio

**Fase 3: 50% de tráfego** (8-12 horas)
- Metade do tráfego na nova versão
- Monitoramento intensivo
- Comparar versões

**Fase 4: 100% de tráfego**
- Completar migração
- Desligar versão antiga
- Manter por 24h para rollback

**5.2.3 Smoke Tests em Produção**

Executar testes básicos:

```python
def production_smoke_test():
    """Testes básicos pós-deploy"""

    # 1. Health check
    response = requests.get(f"{PROD_URL}/health")
    assert response.status_code == 200

    # 2. Teste de conversação básica
    response = requests.post(f"{PROD_URL}/chat", json={
        "message": "Olá",
        "user_id": "smoke_test_user"
    })
    assert response.status_code == 200
    assert "response" in response.json()

    # 3. Validar integração crítica
    response = requests.get(f"{PROD_URL}/integrations/health")
    assert all(status == "up" for status in response.json().values())

    # 4. Verificar knowledge base
    response = requests.post(f"{PROD_URL}/search", json={
        "query": "produto"
    })
    assert len(response.json()["results"]) > 0
```

### 5.3 Configuração de Monitoramento

**5.3.1 Métricas de Infraestrutura**

**System Metrics**:
- CPU usage
- Memory usage
- Disk I/O
- Network I/O
- Container health

**Application Metrics**:
- Request rate
- Response time (p50, p95, p99)
- Error rate
- Throughput
- Active connections

**Ferramentas**:
- Prometheus + Grafana
- CloudWatch (AWS)
- Azure Monitor
- Google Cloud Monitoring
- DataDog / New Relic

**5.3.2 Métricas de Negócio**

**Conversação**:
- Total de conversas
- Conversas concluídas
- Taxa de abandono
- Tempo médio de conversa
- Mensagens por conversa

**Comercial**:
- Leads gerados
- Qualificação de leads
- Taxa de conversão
- Ticket médio
- Revenue gerado

**Satisfação**:
- CSAT score
- NPS
- Thumbs up/down
- Escalações para humano

**5.3.3 Métricas de IA**

**Quality**:
- Intent accuracy
- Entity extraction precision
- Response relevance score
- Hallucination rate

**Performance**:
- LLM latency
- Token usage
- Cache hit rate
- Retrieval accuracy

**Cost**:
- Token cost per conversation
- API costs
- Compute costs

**5.3.4 Dashboards**

**Dashboard Operacional**:
```
┌─────────────────────────────────────────┐
│ Status Geral          │ ✅ Healthy      │
├─────────────────────────────────────────┤
│ Uptime (24h)          │ 99.95%          │
│ Active Users          │ 1,234           │
│ Conversations/hour    │ 456             │
│ Avg Response Time     │ 1.2s            │
│ Error Rate            │ 0.3%            │
├─────────────────────────────────────────┤
│ Integrations                            │
│ ├─ CRM               │ ✅ Up           │
│ ├─ Payment           │ ✅ Up           │
│ └─ Email             │ ✅ Up           │
└─────────────────────────────────────────┘
```

**Dashboard de Negócio**:
```
┌─────────────────────────────────────────┐
│ Hoje              │ Semana  │ Mês       │
├─────────────────────────────────────────┤
│ Leads Gerados                           │
│ 45                │ 312     │ 1,205     │
├─────────────────────────────────────────┤
│ Conversões                              │
│ 12                │ 89      │ 342       │
├─────────────────────────────────────────┤
│ Taxa Conversão                          │
│ 26.7%             │ 28.5%   │ 28.4%     │
├─────────────────────────────────────────┤
│ Revenue                                 │
│ R$ 15.400         │ R$ 98k  │ R$ 385k   │
└─────────────────────────────────────────┘
```

**Template**: `templates/monitoramento/dashboards.json`

### 5.4 Configuração de Alertas

**5.4.1 Alertas Críticos (P0)**

Requerem ação imediata:

```yaml
alerts:
  - name: service_down
    condition: uptime < 95%
    severity: critical
    notification: pager, sms, call
    response_time: 15min

  - name: high_error_rate
    condition: error_rate > 5%
    severity: critical
    notification: pager, sms
    response_time: 15min

  - name: integration_failure
    condition: integration_errors > 10/min
    severity: critical
    notification: pager, slack
    response_time: 30min
```

**5.4.2 Alertas Importantes (P1)**

Requerem atenção em horas:

```yaml
  - name: high_latency
    condition: p95_response_time > 3s
    severity: high
    notification: slack, email
    response_time: 2h

  - name: increased_error_rate
    condition: error_rate > 2%
    severity: high
    notification: slack, email
    response_time: 2h

  - name: low_satisfaction
    condition: csat < 3.5
    severity: high
    notification: email
    response_time: 4h
```

**5.4.3 Alertas de Monitoramento (P2)**

Para análise:

```yaml
  - name: unusual_traffic
    condition: requests > 150% of avg
    severity: medium
    notification: email
    response_time: 1 day

  - name: cost_spike
    condition: daily_cost > 120% of avg
    severity: medium
    notification: email
    response_time: 1 day
```

**5.4.4 Canais de Notificação**

- **PagerDuty**: Alertas críticos
- **Slack**: Canal #alerts-production
- **Email**: Time técnico
- **SMS**: On-call engineer
- **Dashboard**: Always visible

### 5.5 Logging e Tracing

**5.5.1 Logging Estruturado**

```python
import structlog

logger = structlog.get_logger()

logger.info(
    "conversation_started",
    user_id=user_id,
    session_id=session_id,
    channel="whatsapp",
    timestamp=datetime.utcnow()
)

logger.info(
    "intent_detected",
    user_id=user_id,
    session_id=session_id,
    intent="pricing_inquiry",
    confidence=0.95
)

logger.info(
    "integration_call",
    integration="crm",
    operation="create_lead",
    duration_ms=234,
    status="success"
)
```

**5.5.2 Log Aggregation**

Centralizar logs:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Splunk**
- **CloudWatch Logs**
- **Datadog Logs**

**5.5.3 Distributed Tracing**

Rastrear requests através do sistema:

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("process_conversation"):
    with tracer.start_as_current_span("classify_intent"):
        intent = classify(message)

    with tracer.start_as_current_span("retrieve_context"):
        context = get_context(user_id)

    with tracer.start_as_current_span("generate_response"):
        response = llm.generate(intent, context)

    with tracer.start_as_current_span("save_interaction"):
        save_to_db(interaction)
```

**Ferramentas**:
- Jaeger
- Zipkin
- LangSmith
- LangFuse

### 5.6 Treinamento da Equipe

**5.6.1 Documentação de Operação**

**Runbook** deve incluir:

1. **Visão Geral do Sistema**
   - Arquitetura
   - Componentes
   - Integrações

2. **Operações Comuns**
   - Como fazer deploy
   - Como fazer rollback
   - Como escalar

3. **Troubleshooting**
   - Problemas comuns
   - Como diagnosticar
   - Como resolver

4. **Procedimentos de Emergência**
   - Quem contatar
   - Escalação
   - Recovery procedures

5. **FAQs**
   - Questões frequentes
   - Respostas rápidas

**Template**: `docs/operacao/runbook.md`

**5.6.2 Sessão de Treinamento**

**Para equipe de atendimento**:
- Como o sistema funciona
- Quando agente escala
- Como assumir conversa
- Dashboard de monitoramento
- Casos comuns

**Para equipe técnica**:
- Arquitetura detalhada
- Como fazer deploy
- Monitoramento e alertas
- Troubleshooting
- Escalação de issues

**5.6.3 On-call Setup**

Estabelecer rotação on-call:
- Schedule de plantão
- Playbooks para issues comuns
- Escalation path
- Tools e acessos necessários

### 5.7 Go-Live Communication

**5.7.1 Comunicação Interna**

Email para stakeholders:

```
Assunto: [PROD] Agentes de IA - Go-Live Concluído

Olá time,

O deploy dos agentes de IA para atendimento comercial foi
concluído com sucesso às 14:30 de hoje.

Status:
✅ Deploy completado sem erros
✅ Smoke tests passando
✅ Integrações funcionando
✅ Monitoramento ativo

Métricas iniciais (primeiras 2h):
- 23 conversas processadas
- Response time médio: 1.1s
- Zero erros
- CSAT: 4.8/5 (4 respostas)

Dashboards:
- Operacional: https://grafana.../operational
- Negócio: https://grafana.../business

Suporte:
- Slack: #agents-support
- On-call: João Silva (tel: ...)

[Time]
```

**5.7.2 Comunicação Externa**

Se aplicável, anunciar para clientes:
- Email marketing
- Post em redes sociais
- Update no site
- In-app notification

### 5.8 Monitoramento Pós-Deploy

**5.8.1 War Room (Primeiras 24h)**

Time em standby para resolver issues:
- Monitor dashboards continuamente
- Resposta rápida a alertas
- Validação de métricas de negócio
- Documentação de incidents

**5.8.2 Período de Observação**

**Semana 1**:
- Monitoramento intensivo
- Daily review de métricas
- Ajustes rápidos se necessário
- Coleta de feedback

**Semana 2-4**:
- Monitoramento regular
- Weekly review
- Análise de tendências
- Planejamento de otimizações

**5.8.3 Métricas de Sucesso**

Validar após 30 dias:

**Disponibilidade**:
- [ ] Uptime >= 99.5%
- [ ] p95 response time < 2s
- [ ] Error rate < 1%

**Negócio**:
- [ ] Taxa conversão >= target
- [ ] Volume de leads >= target
- [ ] CSAT >= 4.0

**Operação**:
- [ ] Zero incidents P0
- [ ] < 3 incidents P1
- [ ] Time to resolution < SLA

## Saídas

- ✅ Deploy em produção concluído
- ✅ Monitoramento ativo
- ✅ Alertas configurados
- ✅ Dashboards disponíveis
- ✅ Logging centralizado
- ✅ Tracing implementado
- ✅ Equipe treinada
- ✅ Runbook documentado
- ✅ Comunicação realizada
- ✅ Sistema estável

## Critérios de Aceite

- [ ] Deploy executado com sucesso
- [ ] Smoke tests passando
- [ ] Todas as integrações funcionando
- [ ] Monitoramento capturando métricas
- [ ] Alertas testados e funcionando
- [ ] Equipe treinada
- [ ] Runbook completo e validado
- [ ] Sistema estável por 72h
- [ ] Métricas dentro do esperado
- [ ] Cliente notificado e satisfeito

## Duração Estimada

**Deploy**: 4-8 horas
**Monitoramento inicial**: 72 horas
**Período de observação**: 30 dias

## Próximo Processo

[06 - Melhoria Contínua](06-melhoria-continua.md)
