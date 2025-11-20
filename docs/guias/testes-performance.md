# Guia: Testes de Performance

## Visão Geral

Testes de performance garantem que o sistema suporta carga esperada com latência aceitável. Este guia ensina load testing, stress testing e benchmarking.

## Ferramentas

### Locust (Load Testing)

```python
# locustfile.py
from locust import HttpUser, task, between

class AgentUser(HttpUser):
    wait_time = between(1, 3)  # Pausa entre requests

    @task(3)  # Peso 3 (mais frequente)
    def send_message(self):
        """Simula envio de mensagem."""
        self.client.post("/api/chat", json={
            "message": "Olá, quero informações sobre CRM",
            "session_id": f"session_{self.environment.runner.user_count}"
        })

    @task(1)  # Peso 1 (menos frequente)
    def get_history(self):
        """Simula busca de histórico."""
        self.client.get(f"/api/sessions/session_1/history")

# Executar:
# locust -f locustfile.py --host=http://localhost:8000
# Abrir http://localhost:8089
```

### pytest-benchmark

```python
# tests/performance/test_benchmarks.py
import pytest

def test_agent_response_time(benchmark, agent):
    """Benchmark de tempo de resposta."""
    result = benchmark(agent.process, "Olá", {"user_id": "test"})

    # Deve responder em < 2s
    assert benchmark.stats['mean'] < 2.0


def test_database_query_performance(benchmark, db):
    """Benchmark de queries."""
    result = benchmark(
        db.conversations.find,
        {"user_id": "test"},
        limit=100
    )

    # Deve completar em < 100ms
    assert benchmark.stats['mean'] < 0.1
```

## Métricas Importantes

### Response Time (Latência)

```python
import time

def measure_latency(func, *args, **kwargs):
    """Mede latência de função."""
    latencies = []

    for _ in range(100):  # 100 requisições
        start = time.time()
        func(*args, **kwargs)
        latency = time.time() - start
        latencies.append(latency)

    return {
        "p50": np.percentile(latencies, 50),
        "p95": np.percentile(latencies, 95),
        "p99": np.percentile(latencies, 99),
        "mean": np.mean(latencies),
        "max": max(latencies)
    }


# Targets
targets = {
    "p50": 1.0,  # 50% em < 1s
    "p95": 2.0,  # 95% em < 2s
    "p99": 5.0   # 99% em < 5s
}
```

### Throughput (Vazão)

```python
def measure_throughput(func, duration_seconds=60):
    """Mede requests por segundo."""
    start = time.time()
    count = 0

    while time.time() - start < duration_seconds:
        func()
        count += 1

    elapsed = time.time() - start
    rps = count / elapsed

    return {
        "total_requests": count,
        "duration": elapsed,
        "requests_per_second": rps
    }

# Target: >= 100 req/s
```

## Load Testing Scenarios

### Cenário 1: Load Normal

```python
# 100 usuários simultâneos
# 10 req/s por usuário
# Duração: 10 minutos

locust -f locustfile.py \
    --host=http://production.com \
    --users=100 \
    --spawn-rate=10 \
    --run-time=10m \
    --headless
```

### Cenário 2: Pico de Tráfego

```python
# Simular Black Friday
# 1000 usuários simultâneos
# 30 min de teste

locust -f locustfile.py \
    --users=1000 \
    --spawn-rate=50 \
    --run-time=30m \
    --headless
```

### Cenário 3: Stress Test

```python
# Aumentar carga até quebrar
class StressTest(HttpUser):
    wait_time = constant(0)  # Sem pausa

    @task
    def stress(self):
        self.client.post("/api/chat", json={"message": "test"})

# Aumentar usuários gradualmente até sistema falhar
```

## Otimizações

### Caching

```python
from functools import lru_cache
import redis

redis_client = redis.Redis()

@lru_cache(maxsize=1000)
def get_product_info(product_id):
    """Cache em memória."""
    return fetch_from_database(product_id)


def get_with_redis_cache(key):
    """Cache distribuído."""
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)

    data = expensive_operation()
    redis_client.setex(key, 300, json.dumps(data))  # 5 min TTL
    return data
```

### Database Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # Conexões permanentes
    max_overflow=40,       # Conexões adicionais sob carga
    pool_pre_ping=True,    # Verificar conexões antes de usar
    pool_recycle=3600      # Reciclar conexões a cada 1h
)
```

### Async Operations

```python
import asyncio
from fastapi import FastAPI

app = FastAPI()

@app.post("/api/chat")
async def chat(message: str):
    """Endpoint assíncrono."""
    # Operações em paralelo
    user_data, product_data = await asyncio.gather(
        fetch_user_data_async(user_id),
        fetch_product_data_async()
    )

    response = await agent.process_async(message, user_data)
    return response
```

## Monitoramento de Performance

```python
# Instrumentação com Prometheus
from prometheus_client import Counter, Histogram

request_count = Counter('http_requests_total', 'Total HTTP Requests')
request_latency = Histogram('http_request_duration_seconds', 'HTTP Request Latency')

@request_latency.time()
def process_request():
    request_count.inc()
    # ... processar request
```

## Troubleshooting Performance

### CPU Alto

```bash
# Identificar hotspots
python -m cProfile -o profile.stats main.py

# Visualizar
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative')
p.print_stats(20)
```

### Memória Alta

```python
import tracemalloc

tracemalloc.start()

# Código aqui

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

for stat in top_stats[:10]:
    print(stat)
```

### Database Lento

```sql
-- PostgreSQL: Queries lentas
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Adicionar índices
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
```

## Próximos Passos

- [Monitoramento](monitoramento.md)
- [Otimização de Custos](otimizacao-custos.md)

## Referências

- [Locust Documentation](https://docs.locust.io/)
- [pytest-benchmark](https://pytest-benchmark.readthedocs.io/)
