# Guia: Troubleshooting - Resolução de Problemas Comuns

## Visão Geral

Este guia lista problemas comuns encontrados durante desenvolvimento, deploy e operação de agentes de IA, com soluções práticas e diagnósticos.

## Índice

1. [Problemas de Setup](#problemas-de-setup)
2. [Problemas com LLM](#problemas-com-llm)
3. [Problemas de Integração](#problemas-de-integração)
4. [Problemas de Performance](#problemas-de-performance)
5. [Problemas em Produção](#problemas-em-produção)
6. [Problemas com Testes](#problemas-com-testes)

## Problemas de Setup

### Erro: "Module not found"

**Sintoma**: `ModuleNotFoundError: No module named 'xyz'`

**Causas**:
- Pacote não instalado
- Ambiente virtual não ativado
- PYTHONPATH incorreto

**Solução**:
```bash
# Verificar venv ativado
which python  # Deve mostrar caminho do venv

# Ativar venv se necessário
source venv/bin/activate

# Instalar pacote faltando
pip install xyz

# Ou reinstalar requirements
pip install -r requirements.txt

# Adicionar ao PYTHONPATH se necessário
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

### Erro: "Permission denied" ao instalar pacotes

**Solução**:
```bash
# NUNCA use sudo pip!
# Use ambiente virtual
python -m venv venv
source venv/bin/activate
pip install pacote
```

### Erro: "SSL Certificate verify failed"

**Solução**:
```bash
# macOS
cd "/Applications/Python 3.11/"
./Install\ Certificates.command

# Ou temporariamente (não recomendado para produção)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pacote
```

## Problemas com LLM

### Erro: "Rate limit exceeded"

**Sintoma**: `RateLimitError: You exceeded your current quota`

**Diagnóstico**:
```python
# Verificar usage
import openai
response = openai.chat.completions.create(...)
print(response.usage)
```

**Solução**:
```python
# 1. Implementar retry com backoff
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5)
)
def call_llm_with_retry():
    return openai.chat.completions.create(...)

# 2. Implementar rate limiter
from integrations.rate_limiter import RateLimiter
limiter = RateLimiter(max_requests=50, time_window=60)

limiter.acquire()
response = openai.chat.completions.create(...)

# 3. Usar tier maior ou verificar billing
# https://platform.openai.com/account/billing
```

### Erro: "Context length exceeded"

**Sintoma**: `InvalidRequestError: This model's maximum context length is 4096 tokens`

**Solução**:
```python
# 1. Truncar histórico de conversa
def truncate_history(messages, max_tokens=3000):
    """Mantém apenas mensagens recentes."""
    # Estimar tokens (aproximação)
    total_tokens = sum(len(m["content"]) // 4 for m in messages)

    while total_tokens > max_tokens and len(messages) > 2:
        # Remover mensagem mais antiga (mantendo system prompt)
        messages.pop(1)
        total_tokens = sum(len(m["content"]) // 4 for m in messages)

    return messages

# 2. Usar modelo com contexto maior
model = "gpt-4-turbo-preview"  # 128k tokens

# 3. Resumir conversas antigas
def summarize_old_messages(messages):
    """Resumir mensagens antigas em uma única mensagem."""
    old_messages = messages[1:-5]  # Manter system e últimas 5
    summary_prompt = "Resumir esta conversa em 2-3 parágrafos: ..."

    summary = call_llm(summary_prompt)

    return [messages[0]] + [{"role": "system", "content": summary}] + messages[-5:]
```

### Resposta muito lenta (> 10s)

**Diagnóstico**:
```python
import time

start = time.time()
response = openai.chat.completions.create(...)
latency = time.time() - start

print(f"Latency: {latency:.2f}s")
```

**Soluções**:
```python
# 1. Reduzir max_tokens
response = openai.chat.completions.create(
    max_tokens=300,  # Ao invés de 1000+
    ...
)

# 2. Usar modelo mais rápido
model = "gpt-3.5-turbo"  # Mais rápido que gpt-4

# 3. Implementar timeout
response = openai.chat.completions.create(
    timeout=10.0,  # Timeout em segundos
    ...
)

# 4. Usar streaming para UX melhor
for chunk in openai.chat.completions.create(stream=True, ...):
    print(chunk.choices[0].delta.content, end="")
```

### Respostas inconsistentes

**Solução**:
```python
# 1. Reduzir temperature
response = openai.chat.completions.create(
    temperature=0.3,  # Mais determinístico (0-1)
    ...
)

# 2. Usar seed (algumas APIs suportam)
response = openai.chat.completions.create(
    seed=42,  # Resultados mais consistentes
    ...
)

# 3. Melhorar prompt (mais específico)
```

## Problemas de Integração

### Erro: "Connection timeout" em API externa

**Diagnóstico**:
```python
import requests
import time

start = time.time()
try:
    response = requests.get(url, timeout=5)
    print(f"Success in {time.time() - start:.2f}s")
except requests.exceptions.Timeout:
    print("Timeout!")
```

**Solução**:
```python
# 1. Aumentar timeout
response = requests.get(url, timeout=30)

# 2. Implementar retry
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

response = session.get(url)

# 3. Implementar fallback
try:
    data = fetch_from_api()
except Timeout:
    data = fetch_from_cache() or get_default_data()
```

### Erro: "Authentication failed" (401)

**Diagnóstico**:
```python
# Verificar API key
print(f"API Key: {api_key[:10]}...")  # Primeiros 10 chars

# Testar manualmente
curl -H "Authorization: Bearer YOUR_KEY" https://api.example.com/endpoint
```

**Solução**:
```python
# 1. Verificar .env
cat .env | grep API_KEY

# 2. Verificar que .env está sendo carregado
from dotenv import load_dotenv
import os

load_dotenv()
print(os.getenv("CRM_API_KEY"))  # Deve imprimir a key

# 3. Verificar formato do header
headers = {
    "Authorization": f"Bearer {api_key}",  # Bearer?
    # Ou
    "X-API-Key": api_key,  # Depende da API
}

# 4. Regenerar API key se expirada
```

### Dados não sincronizando com CRM

**Diagnóstico**:
```python
# Verificar logs
import logging
logging.basicConfig(level=logging.DEBUG)

# Ver request/response completos
response = requests.post(url, json=data)
print(f"Request: {data}")
print(f"Response: {response.text}")
print(f"Status: {response.status_code}")
```

**Solução**:
```python
# 1. Validar mapeamento de campos
def validate_mapping(internal_data, api_format):
    """Verificar se todos campos obrigatórios estão presentes."""
    required_fields = ["Company", "Email", "Phone"]

    for field in required_fields:
        if field not in api_format or not api_format[field]:
            raise ValueError(f"Missing required field: {field}")

# 2. Verificar formato de dados
# API pode esperar tipos específicos
data = {
    "NumberOfEmployees": int(company_size),  # Não string!
    "Budget": float(budget),
    "Email": email.lower().strip()
}

# 3. Implementar webhook para confirmar sync
# 4. Verificar permissões da API key
```

## Problemas de Performance

### Agente muito lento (> 5s por resposta)

**Diagnóstico**:
```python
import time

# Adicionar timing em cada etapa
start = time.time()
print(f"[{time.time() - start:.2f}s] Validating input...")

is_valid, error = validate_input(user_input)
print(f"[{time.time() - start:.2f}s] Calling LLM...")

response = llm.chat.completions.create(...)
print(f"[{time.time() - start:.2f}s] Applying guardrails...")

# Identificar gargalo
```

**Soluções**:
```python
# 1. Usar modelo mais rápido para tasks simples
if is_simple_query(user_input):
    model = "gpt-3.5-turbo"
else:
    model = "gpt-4"

# 2. Implementar caching
from functools import lru_cache

@lru_cache(maxsize=100)
def get_product_info(product_id):
    return fetch_from_api(product_id)

# 3. Paralelizar operações independentes
import asyncio

async def process_parallel():
    results = await asyncio.gather(
        fetch_user_data(user_id),
        fetch_product_catalog(),
        fetch_pricing()
    )
    return results

# 4. Otimizar prompts (menos tokens)
```

### Alto uso de memória

**Diagnóstico**:
```python
import tracemalloc

tracemalloc.start()

# Seu código aqui
process_conversation()

current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 10**6:.1f} MB")
print(f"Peak: {peak / 10**6:.1f} MB")

tracemalloc.stop()
```

**Solução**:
```python
# 1. Limpar histórico antigo
def cleanup_old_conversations(max_age_hours=24):
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    db.conversations.delete_many({"timestamp": {"$lt": cutoff}})

# 2. Limitar tamanho de cache
from cachetools import LRUCache
cache = LRUCache(maxsize=100)  # Apenas 100 itens

# 3. Usar generators ao invés de listas
def get_conversations():
    for conv in db.conversations.find():
        yield conv  # Ao invés de return list()
```

### Database queries lentas

**Diagnóstico**:
```sql
-- PostgreSQL: Ver queries lentas
SELECT query, calls, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**Solução**:
```python
# 1. Adicionar índices
from sqlalchemy import Index

Index('idx_user_id', Conversation.user_id)
Index('idx_timestamp', Conversation.timestamp)

# 2. Usar select específico (não SELECT *)
query = select(Conversation.id, Conversation.message).where(...)

# 3. Implementar paginação
def get_conversations_paginated(page=1, per_page=20):
    offset = (page - 1) * per_page
    return db.query(Conversation).limit(per_page).offset(offset).all()

# 4. Usar connection pooling
from sqlalchemy.pool import QueuePool
engine = create_engine(
    url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

## Problemas em Produção

### Erro: "Out of memory" (OOM)

**Solução imediata**:
```bash
# Reiniciar serviço
sudo systemctl restart agente-service

# Ver logs
journalctl -u agente-service -n 100
```

**Solução permanente**:
```python
# 1. Implementar limites de memória
# docker-compose.yml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 2G

# 2. Configurar garbage collection
import gc
gc.collect()  # Forçar coleta

# 3. Usar worker process model
# gunicorn com múltiplos workers
gunicorn -w 4 -k uvicorn.workers.UvicornWorker --max-requests 1000 main:app
```

### Respostas diferentes entre staging e produção

**Diagnóstico**:
```bash
# Comparar configurações
diff .env.staging .env.production

# Comparar versões de dependências
pip freeze > staging_deps.txt
# No prod:
pip freeze > prod_deps.txt
diff staging_deps.txt prod_deps.txt
```

**Solução**:
```bash
# 1. Usar mesma versão de deps
pip install -r requirements-lock.txt

# 2. Verificar variáveis de ambiente
echo $OPENAI_API_KEY | head -c 20

# 3. Verificar modelo LLM usado
# Staging pode estar usando modelo diferente

# 4. Sincronizar dados de teste
```

### Logs não aparecem

**Solução**:
```python
# 1. Configurar logging corretamente
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()  # Para stdout
    ]
)

# 2. Verificar destino dos logs
# No Docker, logs vão para stdout
import sys
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# 3. Ver logs em produção
docker logs -f container_name
# Ou
kubectl logs -f pod_name
```

## Problemas com Testes

### Testes passam localmente mas falham no CI

**Diagnóstico**:
```bash
# Rodar localmente da mesma forma que CI
docker run -it --rm -v $(pwd):/app python:3.11 bash
cd /app
pip install -r requirements.txt
pytest
```

**Solução**:
```python
# 1. Fixar seeds aleatórios
import random
import numpy as np

random.seed(42)
np.random.seed(42)

# 2. Mockar datetime
from unittest.mock import patch
from datetime import datetime

@patch('module.datetime')
def test_something(mock_datetime):
    mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0)
    # Teste aqui

# 3. Usar fixtures para dados consistentes
@pytest.fixture
def fixed_data():
    return {"key": "value"}  # Sempre mesmos dados
```

### Testes muito lentos

**Solução**:
```python
# 1. Marcar testes lentos
@pytest.mark.slow
def test_full_integration():
    ...

# Rodar sem testes lentos
pytest -m "not slow"

# 2. Usar mocks ao invés de APIs reais
@patch('integrations.crm_client.CRMClient.create_lead')
def test_lead_creation(mock_create_lead):
    mock_create_lead.return_value = {"success": True, "lead_id": "123"}
    # Teste instantâneo

# 3. Paralelizar testes
pip install pytest-xdist
pytest -n auto  # Usa todos CPUs
```

### Coverage baixo

**Solução**:
```bash
# 1. Ver quais linhas não estão cobertas
pytest --cov=src --cov-report=html
open htmlcov/index.html

# 2. Adicionar testes para linhas descobertas

# 3. Focar em código crítico primeiro
pytest --cov=src/agents --cov-report=term-missing

# 4. Ignorar arquivos de config/migrations
# .coveragerc
[run]
omit =
    */tests/*
    */migrations/*
    */config/*
```

## Ferramentas de Diagnóstico

### Script de Health Check

```python
# scripts/health_check.py
"""
Verifica saúde de todos componentes.
"""

def check_llm():
    """Testa conexão com LLM."""
    try:
        import openai
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        return True, "LLM OK"
    except Exception as e:
        return False, f"LLM Error: {e}"


def check_database():
    """Testa conexão com database."""
    try:
        from sqlalchemy import create_engine
        engine = create_engine(os.getenv("DATABASE_URL"))
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True, "Database OK"
    except Exception as e:
        return False, f"Database Error: {e}"


def check_redis():
    """Testa conexão com Redis."""
    try:
        import redis
        r = redis.from_url(os.getenv("REDIS_URL"))
        r.ping()
        return True, "Redis OK"
    except Exception as e:
        return False, f"Redis Error: {e}"


def check_external_apis():
    """Testa APIs externas."""
    try:
        from integrations.crm_client import CRMClient
        client = CRMClient()
        client.health_check()
        return True, "External APIs OK"
    except Exception as e:
        return False, f"External APIs Error: {e}"


if __name__ == "__main__":
    checks = [
        check_llm,
        check_database,
        check_redis,
        check_external_apis
    ]

    all_passed = True
    for check in checks:
        passed, message = check()
        status = "✓" if passed else "✗"
        print(f"{status} {message}")

        if not passed:
            all_passed = False

    sys.exit(0 if all_passed else 1)
```

## Próximos Passos

- [Monitoramento](monitoramento.md): Detectar problemas antes
- [Deploy](deploy.md): Deploy seguro
- [Setup Ambiente](setup-ambiente.md): Setup correto

## Referências

- [Python Debugging](https://realpython.com/python-debugging-pdb/)
- [Docker Troubleshooting](https://docs.docker.com/config/daemon/logs/)
