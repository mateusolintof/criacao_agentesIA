# Guia: Otimização de Custos

## Visão Geral

Reduzir custos mantendo qualidade é essencial para sustentabilidade. Este guia ensina estratégias para otimizar custos com LLM, infraestrutura e operação.

## Anatomia de Custos

```
Total = LLM Costs + Infrastructure + Monitoring + Databases + External APIs

Típico:
- LLM: 60-70%
- Infrastructure: 20-25%
- External APIs: 5-10%
- Databases/Storage: 3-5%
- Monitoring: 2-3%
```

## Otimização de Custos com LLM

### 1. Escolher Modelo Apropriado

```python
# Roteamento inteligente de modelo
def select_model(task_complexity: str, input_length: int):
    """Seleciona modelo baseado em complexidade."""

    # Tasks simples: modelo barato
    if task_complexity == "simple" and input_length < 500:
        return "gpt-3.5-turbo"  # $0.001/1K tokens

    # Tasks médias: modelo intermediário
    elif task_complexity == "medium":
        return "gpt-4-turbo"  # $0.01/1K tokens

    # Tasks complexas: modelo premium
    else:
        return "gpt-4"  # $0.03/1K tokens


# Economia: 70-90% em tasks simples
```

### 2. Reduzir Tokens

```python
# Otimizar prompts
# ❌ Ruim (500 tokens):
prompt = """
Você é um assistente muito útil e amigável que ajuda usuários
com todas as suas dúvidas sobre produtos. Sempre seja educado,
respeitoso e forneça informações detalhadas...
[continua por muitas linhas]
"""

# ✅ Bom (100 tokens):
prompt = """
Assistente de produtos. Seja conciso e útil.
"""

# Economia: 80% nos tokens do system prompt
```

### 3. Caching Agressivo

```python
import hashlib
from functools import lru_cache

# Cache em memória
@lru_cache(maxsize=1000)
def get_llm_response_cached(prompt_hash: str):
    return cached_responses.get(prompt_hash)


def process_with_cache(user_input: str, system_prompt: str):
    """Usa cache para perguntas similares."""

    # Hash do input
    input_hash = hashlib.md5(user_input.lower().encode()).hexdigest()

    # Verificar cache
    cached = get_llm_response_cached(input_hash)
    if cached:
        return cached  # $0

    # Chamar LLM
    response = call_llm(system_prompt, user_input)  # $$$

    # Armazenar
    cache_response(input_hash, response)

    return response

# Cache hit rate 30%+ = 30% economia
```

### 4. Limitar max_tokens

```python
# Controlar tamanho da resposta
response = openai.chat.completions.create(
    model="gpt-4",
    messages=messages,
    max_tokens=150,  # Ao invés de 1000+
    temperature=0.7
)

# Economia: 50-85% dependendo do caso
```

### 5. Usar Embeddings Locais

```python
# ❌ Custoso: OpenAI Embeddings
from langchain.embeddings import OpenAIEmbeddings
embeddings = OpenAIEmbeddings()  # $0.0001 per 1K tokens

# ✅ Gratuito: Sentence Transformers (local)
from langchain.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)  # $0

# Para 1M documentos: $100+ vs $0
```

### 6. Batch Processing

```python
# Processar múltiplos inputs em um request
batch_prompt = """
Classifique cada mensagem como: sales, support, product

1. "{message_1}"
2. "{message_2}"
3. "{message_3}"

Retorne JSON: {{"1": "sales", "2": "support", "3": "product"}}
"""

# 1 request ao invés de 3 = 66% economia
```

## Otimização de Infraestrutura

### 1. Right-Sizing

```yaml
# ❌ Over-provisioned
resources:
  requests:
    memory: "4Gi"    # Usando apenas 1Gi
    cpu: "2000m"     # Usando apenas 500m

# ✅ Optimized
resources:
  requests:
    memory: "1.5Gi"  # 20% buffer
    cpu: "600m"      # 20% buffer

# Economia: 50-70%
```

### 2. Auto-Scaling Inteligente

```yaml
# HPA com métricas customizadas
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 2      # Não 5
  maxReplicas: 10     # Não 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # Não 50

# Economia: 30-40% em recursos idle
```

### 3. Spot Instances

```yaml
# Kubernetes: Usar spot instances para workloads tolerantes
nodeSelector:
  node-type: spot  # AWS Spot = 70% desconto

# Para processamento em batch, background jobs
```

### 4. Database Otimizações

```python
# ❌ N+1 Queries
for conversation in conversations:
    user = db.query(User).get(conversation.user_id)  # N queries

# ✅ Eager Loading
conversations = db.query(Conversation).options(
    joinedload(Conversation.user)
).all()  # 1 query

# Economia: 80-90% em DB costs
```

## Otimização de APIs Externas

### 1. Rate Limiting Interno

```python
# Limitar calls para APIs pagas
class RateLimitedAPI:
    def __init__(self, max_calls_per_day: int):
        self.max_calls = max_calls_per_day
        self.calls_today = 0
        self.last_reset = datetime.now().date()

    def call_api(self, *args):
        # Reset contador diário
        if datetime.now().date() > self.last_reset:
            self.calls_today = 0
            self.last_reset = datetime.now().date()

        # Verificar limite
        if self.calls_today >= self.max_calls:
            return self._get_cached_or_fallback()

        # Fazer call
        self.calls_today += 1
        return self._real_api_call(*args)
```

### 2. Consolidar Chamadas

```python
# ❌ Múltiplas chamadas
product_1 = api.get_product(id_1)
product_2 = api.get_product(id_2)
product_3 = api.get_product(id_3)

# ✅ Batch request
products = api.get_products_batch([id_1, id_2, id_3])

# Economia: 66%
```

## Monitoramento de Custos

### Cost Tracking

```python
from prometheus_client import Counter

# Track costs
llm_cost_usd = Counter('llm_cost_usd_total', 'Custo total com LLM')
api_cost_usd = Counter('api_cost_usd_total', 'Custo com APIs externas')

# Calcular custo
def calculate_llm_cost(usage):
    """Calcula custo baseado em usage."""
    pricing = {
        "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
        "gpt-3.5-turbo": {"input": 0.001, "output": 0.002}
    }

    model = usage.model
    input_cost = (usage.prompt_tokens / 1000) * pricing[model]["input"]
    output_cost = (usage.completion_tokens / 1000) * pricing[model]["output"]

    total_cost = input_cost + output_cost
    llm_cost_usd.inc(total_cost)

    return total_cost


# Dashboard de custos
def get_daily_cost():
    """Retorna custo diário."""
    llm = get_metric('llm_cost_usd_total')
    apis = get_metric('api_cost_usd_total')
    infra = get_infra_cost()  # Da AWS/GCP

    return {
        "llm": llm,
        "apis": apis,
        "infrastructure": infra,
        "total": llm + apis + infra
    }
```

### Budget Alerts

```python
# Alertar se custo diário > budget
DAILY_BUDGET = 100  # USD

daily_cost = get_daily_cost()["total"]

if daily_cost > DAILY_BUDGET:
    alert_team(
        f"Cost alert: ${daily_cost:.2f} (budget: ${DAILY_BUDGET})"
    )

    # Auto-scaling down se necessário
    if daily_cost > DAILY_BUDGET * 1.5:
        scale_down_infrastructure()
```

## Estratégias por Budget

### Startup (< $500/mês)

```python
# Prioridades:
# 1. Usar gpt-3.5-turbo sempre que possível
# 2. Embeddings locais (Sentence Transformers)
# 3. Cache agressivo (Redis)
# 4. Single instance (sem auto-scaling)
# 5. PostgreSQL em free tier

config = {
    "default_model": "gpt-3.5-turbo",
    "embeddings": "local",
    "cache_ttl": 7200,  # 2 horas
    "min_replicas": 1,
    "max_replicas": 2
}
```

### Scale-up ($1K-$5K/mês)

```python
# Adicionar:
# 1. Roteamento de modelo (gpt-4 para complex tasks)
# 2. Auto-scaling moderado
# 3. Database otimizado (connection pooling)

config = {
    "model_routing": True,
    "fallback_model": "gpt-3.5-turbo",
    "premium_model": "gpt-4",
    "min_replicas": 2,
    "max_replicas": 5
}
```

### Enterprise (> $10K/mês)

```python
# Investir em:
# 1. Fine-tuning de modelos (menor custo long-term)
# 2. Self-hosted LLMs para tasks simples
# 3. Advanced caching (Vector cache)
# 4. Reserved infrastructure

config = {
    "use_fine_tuned": True,
    "self_hosted_for_simple": True,
    "vector_cache": True,
    "reserved_instances": True
}
```

## ROI de Otimizações

```python
# Calcular ROI de cada otimização
optimizations = {
    "Model routing": {
        "implementation_hours": 8,
        "monthly_savings": 300,
        "roi_months": 8 / (300 / (80 * 4))  # ~0.8 meses
    },
    "Aggressive caching": {
        "implementation_hours": 16,
        "monthly_savings": 200,
        "roi_months": 16 / (200 / (80 * 4))  # ~1.6 meses
    },
    "Local embeddings": {
        "implementation_hours": 4,
        "monthly_savings": 150,
        "roi_months": 4 / (150 / (80 * 4))  # ~0.3 meses
    }
}

# Priorizar por ROI
sorted_optimizations = sorted(
    optimizations.items(),
    key=lambda x: x[1]["roi_months"]
)
```

## Próximos Passos

- [Monitoramento](monitoramento.md): Tracking de custos
- [Deploy](deploy.md): Deploy eficiente

## Referências

- [OpenAI Pricing](https://openai.com/pricing)
- [AWS Cost Optimization](https://aws.amazon.com/pricing/cost-optimization/)
