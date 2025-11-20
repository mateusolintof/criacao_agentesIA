# Guia: Deploy de Agentes de IA

## Visão Geral

Deploy seguro e escalável de agentes em produção. Este guia cobre estratégias de deploy, infraestrutura, CI/CD e rollback.

## Estratégias de Deploy

### 1. Canary Deployment (Recomendado)

```
Deploy gradual minimiza risco:
5% → Monitor 2-4h → 25% → Monitor → 50% → 100%
```

**Implementação**:
```python
# Usar feature flags
from feature_flags import get_flag

def route_to_agent():
    """Roteia para versão nova ou antiga."""
    rollout_percentage = get_flag("new_agent_rollout")  # 5, 25, 50, 100

    if random.random() * 100 < rollout_percentage:
        return new_agent
    else:
        return current_agent
```

### 2. Blue-Green Deployment

```
Blue (atual) ← 100% tráfego
Green (novo) ← 0% tráfego

Trocar: Green ← 100%, Blue ← 0%
```

**Implementação (Kubernetes)**:
```yaml
# Service aponta para deployment ativo
apiVersion: v1
kind: Service
metadata:
  name: agent-service
spec:
  selector:
    app: agent
    version: blue  # Trocar para green quando pronto
```

## Infraestrutura

### Docker

```dockerfile
# Dockerfile (Production)
FROM python:3.11-slim

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Usuário não-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Comando
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", "--timeout", "120", "src.main:app"]
```

### Kubernetes

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-deployment
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: agent
  template:
    metadata:
      labels:
        app: agent
    spec:
      containers:
      - name: agent
        image: myregistry/agent:v1.2.3
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: agent-service
spec:
  selector:
    app: agent
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: agent-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: agent-deployment
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest tests/ --cov=src --cov-fail-under=80

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build Docker image
        run: |
          docker build -t myregistry/agent:${{ github.ref_name }} .
          docker tag myregistry/agent:${{ github.ref_name }} myregistry/agent:latest

      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push myregistry/agent:${{ github.ref_name }}
          docker push myregistry/agent:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/agent-deployment \
            agent=myregistry/agent:${{ github.ref_name }}

      - name: Monitor rollout
        run: |
          kubectl rollout status deployment/agent-deployment --timeout=5m

      - name: Run smoke tests
        run: |
          python scripts/smoke_tests.py --url https://production.com
```

## Pre-Deploy Checklist

```markdown
## Pre-Deploy Checklist

### Code
- [ ] Todos testes passando (unit, integration, e2e)
- [ ] Coverage >= 80%
- [ ] Code review aprovado
- [ ] Sem secrets hardcoded
- [ ] Versão atualizada (git tag)

### Infrastructure
- [ ] Secrets configurados (Kubernetes Secrets ou AWS Secrets Manager)
- [ ] Variáveis de ambiente corretas
- [ ] Resource limits adequados (CPU, memória)
- [ ] Auto-scaling configurado

### Monitoring
- [ ] Dashboards criados/atualizados
- [ ] Alertas configurados
- [ ] Logging funcionando

### Documentation
- [ ] Runbook atualizado
- [ ] Changelog atualizado
- [ ] API docs atualizadas (se aplicável)

### Rollback Plan
- [ ] Versão anterior identificada
- [ ] Comando de rollback testado
- [ ] Time de on-call notificado

### Communication
- [ ] Stakeholders notificados
- [ ] Janela de manutenção agendada (se necessário)
- [ ] Status page atualizado
```

## Secrets Management

### Kubernetes Secrets

```bash
# Criar secret
kubectl create secret generic agent-secrets \
  --from-literal=openai-api-key="sk-..." \
  --from-literal=crm-api-key="..." \
  --from-literal=database-url="postgresql://..."

# Usar no deployment
env:
- name: OPENAI_API_KEY
  valueFrom:
    secretKeyRef:
      name: agent-secrets
      key: openai-api-key
```

### AWS Secrets Manager

```python
import boto3
import json

def get_secrets():
    """Carrega secrets do AWS Secrets Manager."""
    client = boto3.client('secretsmanager', region_name='us-east-1')

    response = client.get_secret_value(SecretId='prod/agent/secrets')
    secrets = json.loads(response['SecretString'])

    return secrets

# Uso
secrets = get_secrets()
OPENAI_API_KEY = secrets['OPENAI_API_KEY']
```

## Health Checks

```python
from fastapi import FastAPI, status

app = FastAPI()

@app.get("/health")
def health_check():
    """Health check básico."""
    return {"status": "healthy"}


@app.get("/ready")
def readiness_check():
    """Readiness check - verifica dependências."""
    checks = {
        "database": check_database(),
        "redis": check_redis(),
        "llm": check_llm_api()
    }

    all_healthy = all(checks.values())

    return {
        "ready": all_healthy,
        "checks": checks
    }, status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE


def check_database():
    """Verifica conexão com database."""
    try:
        db.execute("SELECT 1")
        return True
    except:
        return False


def check_llm_api():
    """Verifica API do LLM."""
    try:
        openai.models.list()  # Quick check
        return True
    except:
        return False
```

## Rollback

### Kubernetes Rollback

```bash
# Ver histórico de deployments
kubectl rollout history deployment/agent-deployment

# Rollback para versão anterior
kubectl rollout undo deployment/agent-deployment

# Rollback para revisão específica
kubectl rollout undo deployment/agent-deployment --to-revision=2

# Verificar status
kubectl rollout status deployment/agent-deployment
```

### Rollback Automático

```yaml
# Implementar rollback automático se falhar
apiVersion: argoproj.io/v1alpha1
kind: Rollout
spec:
  strategy:
    canary:
      steps:
      - setWeight: 20
      - pause: {duration: 10m}
      - setWeight: 50
      - pause: {duration: 10m}
      analysis:
        templates:
        - templateName: error-rate
        startingStep: 1
      rollbackWindow:
        activeDeadlineSeconds: 600  # Rollback se falhar em 10 min
```

## Smoke Tests

```python
# scripts/smoke_tests.py
"""
Smoke tests pós-deploy.
"""

import requests
import sys

def test_health(base_url):
    """Testa endpoint de health."""
    response = requests.get(f"{base_url}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_basic_conversation(base_url):
    """Testa conversação básica."""
    response = requests.post(
        f"{base_url}/api/chat",
        json={"message": "Olá", "session_id": "smoke_test"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 0


def test_integration_crm(base_url):
    """Testa integração com CRM."""
    response = requests.get(f"{base_url}/api/integrations/crm/status")
    assert response.status_code == 200
    assert response.json()["connected"] is True


if __name__ == "__main__":
    base_url = sys.argv[1]

    tests = [
        test_health,
        test_basic_conversation,
        test_integration_crm
    ]

    print(f"Running smoke tests on {base_url}...")

    for test in tests:
        try:
            test(base_url)
            print(f"✓ {test.__name__}")
        except Exception as e:
            print(f"✗ {test.__name__}: {e}")
            sys.exit(1)

    print("All smoke tests passed!")
```

## Monitoramento Pós-Deploy

```python
# Monitorar métricas críticas primeiras 2 horas
critical_metrics = [
    "error_rate < 1%",
    "p95_latency < 2s",
    "success_rate > 99%",
    "cpu_usage < 70%",
    "memory_usage < 80%"
]

# Alertar se qualquer métrica falhar
for metric in critical_metrics:
    if not check_metric(metric):
        alert_team(f"CRITICAL: {metric} failed after deploy")
        initiate_rollback()
```

## Próximos Passos

- [Monitoramento](monitoramento.md): Setup completo
- [Troubleshooting](troubleshooting.md): Resolver problemas

## Referências

- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [The Twelve-Factor App](https://12factor.net/)
