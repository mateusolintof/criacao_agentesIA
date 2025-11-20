# Guia: Monitoramento e Observabilidade

## Visão Geral

Monitoramento proativo detecta problemas antes de afetar usuários. Este guia cobre métricas, logging, alertas e dashboards.

## Stack de Monitoramento

```
Logs → Loki/CloudWatch
Metrics → Prometheus
Tracing → Jaeger
Dashboards → Grafana
Alerting → AlertManager/PagerDuty
```

## Métricas Essenciais

### 1. Métricas de Negócio

```python
from prometheus_client import Counter, Histogram, Gauge

# Conversações
conversations_total = Counter(
    'conversations_total',
    'Total de conversações',
    ['outcome']  # qualified, unqualified, abandoned
)

# Leads criados
leads_created = Counter('leads_created_total', 'Leads criados no CRM')

# Taxa de conversão
conversion_rate = Gauge('conversion_rate', 'Taxa de conversão')

# Uso
conversations_total.labels(outcome='qualified').inc()
leads_created.inc()
conversion_rate.set(calculate_conversion_rate())
```

### 2. Métricas Técnicas

```python
# Latência de resposta
response_latency = Histogram(
    'response_latency_seconds',
    'Latência de resposta',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Erros
errors_total = Counter(
    'errors_total',
    'Total de erros',
    ['error_type']  # validation, api, llm, database
)

# Uso de LLM
llm_tokens_used = Counter('llm_tokens_used_total', 'Tokens usados')
llm_cost = Counter('llm_cost_total', 'Custo com LLM (USD)')

# Uso
with response_latency.time():
    process_message()

errors_total.labels(error_type='api').inc()
llm_tokens_used.inc(response.usage.total_tokens)
llm_cost.inc(calculate_cost(response.usage))
```

### 3. Métricas de Sistema

```python
# CPU e Memória (coletado automaticamente por Prometheus)

# Conexões de database
db_connections = Gauge('db_connections_active', 'Conexões ativas')

# Queue size
queue_size = Gauge('message_queue_size', 'Mensagens na fila')

# Cache hit rate
cache_hits = Counter('cache_hits_total', 'Cache hits')
cache_misses = Counter('cache_misses_total', 'Cache misses')
```

## Logging Estruturado

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    """Logger com formato estruturado JSON."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log(self, level: str, message: str, **kwargs):
        """Log estruturado."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "service": "agent-service",
            **kwargs
        }

        self.logger.log(
            getattr(logging, level.upper()),
            json.dumps(log_entry)
        )

    def info(self, message: str, **kwargs):
        self.log("info", message, **kwargs)

    def error(self, message: str, **kwargs):
        self.log("error", message, **kwargs)


# Uso
logger = StructuredLogger("agent")

logger.info(
    "Message processed",
    user_id="user_123",
    session_id="session_456",
    latency=1.2,
    tokens_used=150
)
```

## Dashboards (Grafana)

### Dashboard Principal

```json
{
  "dashboard": {
    "title": "Agent Overview",
    "panels": [
      {
        "title": "Conversations per Minute",
        "targets": [
          {
            "expr": "rate(conversations_total[5m])"
          }
        ]
      },
      {
        "title": "Response Latency (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, response_latency_seconds_bucket)"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(errors_total[5m])"
          }
        ]
      },
      {
        "title": "Conversion Rate",
        "targets": [
          {
            "expr": "conversion_rate"
          }
        ]
      }
    ]
  }
}
```

## Alertas

### AlertManager Rules

```yaml
# alerts.yaml
groups:
  - name: agent_alerts
    interval: 30s
    rules:
      # Latência alta
      - alert: HighLatency
        expr: histogram_quantile(0.95, response_latency_seconds_bucket) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Latência p95 acima de 5s"
          description: "Latência atual: {{ $value }}s"

      # Taxa de erro alta
      - alert: HighErrorRate
        expr: rate(errors_total[5m]) > 0.01
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Taxa de erro > 1%"
          description: "Taxa atual: {{ $value }}"

      # Database down
      - alert: DatabaseDown
        expr: db_connections_active == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database sem conexões ativas"

      # LLM API issues
      - alert: LLMAPIFailures
        expr: rate(errors_total{error_type="llm"}[5m]) > 0.05
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "Falhas na API do LLM"

      # Custo alto
      - alert: HighLLMCost
        expr: rate(llm_cost_total[1h]) > 10
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Custo com LLM > $10/hora"
```

### PagerDuty Integration

```python
import requests

def send_pagerduty_alert(severity: str, message: str, details: dict):
    """Envia alerta para PagerDuty."""
    payload = {
        "routing_key": os.getenv("PAGERDUTY_ROUTING_KEY"),
        "event_action": "trigger",
        "payload": {
            "summary": message,
            "severity": severity,
            "source": "agent-service",
            "custom_details": details
        }
    }

    requests.post(
        "https://events.pagerduty.com/v2/enqueue",
        json=payload
    )

# Uso
if error_rate > 0.01:
    send_pagerduty_alert(
        severity="critical",
        message="Error rate above threshold",
        details={"current_rate": error_rate, "threshold": 0.01}
    )
```

## Distributed Tracing

```python
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

tracer = trace.get_tracer(__name__)

@app.post("/api/chat")
async def chat(message: str):
    with tracer.start_as_current_span("process_message"):
        # Span principal

        with tracer.start_as_current_span("validate_input"):
            is_valid = validate(message)

        with tracer.start_as_current_span("call_llm"):
            response = llm.chat.completions.create(...)

        with tracer.start_as_current_span("save_to_db"):
            db.save(response)

        return response
```

## Runbook

```markdown
# Runbook: Operação de Agentes de IA

## Alertas Críticos

### HighErrorRate
**Severidade**: Critical
**Descrição**: Taxa de erro > 1%

**Investigação**:
1. Verificar dashboard de erros por tipo
2. Verificar logs: `kubectl logs -l app=agent --tail=100`
3. Verificar status de integrações externas

**Ação**:
- Se erro de API externa: Verificar status da API
- Se erro de LLM: Verificar quota/billing
- Se erro de database: Verificar conexões/load

**Escalação**: Se não resolver em 15min, escalar para engenharia

### DatabaseDown
**Severidade**: Critical
**Descrição**: Sem conexões com database

**Investigação**:
1. Verificar pods: `kubectl get pods`
2. Testar conexão: `psql -h hostname -U user -d dbname`
3. Verificar secrets: `kubectl get secrets`

**Ação**:
1. Restart pods se necessário
2. Verificar credenciais
3. Verificar networking

**Escalação**: Imediata para DBA

## Deploys

Ver [deploy.md](deploy.md)

## Backups

Ver backup schedule e restore procedure
```

## Próximos Passos

- [Otimização de Custos](otimizacao-custos.md)
- [Troubleshooting](troubleshooting.md)

## Referências

- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Grafana Documentation](https://grafana.com/docs/)
