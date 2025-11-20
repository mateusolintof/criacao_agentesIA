# Runbook Operacional - Agente de IA

**Versão:** 1.0
**Última Atualização:** 2024-01-20
**Público-Alvo:** Engenheiros On-Call, DevOps, SRE
**Tempo Médio de Leitura:** 20 minutos

---

## Índice Rápido

1. [Visão Geral do Sistema](#1-visão-geral-do-sistema)
2. [Arquitetura Rápida](#2-arquitetura-rápida)
3. [Operações Comuns](#3-operações-comuns)
4. [Procedimentos de Incidente](#4-procedimentos-de-incidente)
5. [Guia de Troubleshooting](#5-guia-de-troubleshooting)
6. [Monitoramento e Alertas](#6-monitoramento-e-alertas)
7. [Tarefas de Manutenção](#7-tarefas-de-manutenção)
8. [Procedimentos de Emergência](#8-procedimentos-de-emergência)
9. [Escalação](#9-escalação)
10. [Runbooks Específicos](#10-runbooks-específicos)
11. [Checklist de On-Call](#11-checklist-de-on-call)
12. [Contatos e Recursos](#12-contatos-e-recursos)

---

## 1. Visão Geral do Sistema

### 1.1 O que é o Sistema?

Sistema de agentes de IA conversacionais para atendimento comercial, capaz de:
- Qualificar leads automaticamente
- Responder perguntas sobre produtos/serviços
- Escalar para atendimento humano quando necessário
- Integrar com CRM, email e outras ferramentas

### 1.2 Componentes Principais

| Componente | Função | Tecnologia | Criticidade |
|------------|--------|------------|-------------|
| **Agent API** | API principal do agente | FastAPI + Uvicorn | CRÍTICO |
| **PostgreSQL** | Banco de dados principal | PostgreSQL 15 | CRÍTICO |
| **Redis** | Cache e sessões | Redis 7 | CRÍTICO |
| **LLM Provider** | Geração de respostas | OpenAI/Anthropic | CRÍTICO |
| **CRM Integration** | Sincronização de leads | Salesforce/HubSpot | ALTO |
| **Email Service** | Envio de emails | SendGrid | MÉDIO |
| **Monitoring** | Observabilidade | Prometheus + Grafana | ALTO |

### 1.3 SLAs e Métricas-Alvo

| Métrica | Target | P95 | P99 |
|---------|--------|-----|-----|
| **Uptime** | 99.5% | - | - |
| **Response Time** | <1s | <2s | <3s |
| **Error Rate** | <0.5% | <1% | <2% |
| **Intent Accuracy** | >90% | >85% | >80% |
| **CSAT** | >4.0/5 | >3.5/5 | >3.0/5 |

### 1.4 Ambientes

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Development │ -> │    Test     │ -> │   Staging   │ -> │ Production  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
   Local               CI/CD          Prod-like          Real Users
```

**URLs:**
- Development: `http://localhost:8000`
- Test: `https://test-api.example.com`
- Staging: `https://staging-api.example.com`
- Production: `https://api.example.com`

---

## 2. Arquitetura Rápida

### 2.1 Diagrama de Componentes

```
┌──────────────────────────────────────────────────────┐
│                    USUÁRIOS                          │
│        (Web Chat, WhatsApp, API, Email)              │
└───────────────────┬──────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────┐
│              API GATEWAY (Nginx/ALB)                 │
│  - Auth, Rate Limiting, Load Balancing               │
└───────────────────┬──────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────┐
│            AGENT API (FastAPI)                       │
│  ┌─────────────┐     ┌──────────────────────────┐   │
│  │Router Agent │ --> │ Specialized Agents       │   │
│  └─────────────┘     │ - Sales, Support, etc    │   │
└────────────┬──────────┴──────────┬─────────────────┬─┘
             │                     │                 │
     ┌───────▼──────┐    ┌────────▼─────┐   ┌──────▼─────┐
     │  PostgreSQL  │    │    Redis     │   │  LLM API   │
     │  (Dados)     │    │   (Cache)    │   │ (OpenAI)   │
     └──────────────┘    └──────────────┘   └────────────┘
             │                     │
     ┌───────▼─────────────────────▼──────┐
     │        INTEGRATIONS                │
     │  CRM | Email | Calendar | Analytics│
     └────────────────────────────────────┘
```

### 2.2 Fluxo de Requisição

```
1. User → API Gateway
   └─> Auth check
   └─> Rate limit check
   └─> Route to Agent API

2. Agent API → Process Request
   └─> Validate input (guardrails)
   └─> Load context from Redis/PostgreSQL
   └─> Router Agent classifica intent
   └─> Delega para Specialized Agent

3. Specialized Agent → Generate Response
   └─> Build prompt com context
   └─> Call LLM API
   └─> Execute tools (se necessário)
   └─> Apply guardrails

4. Store & Integrate
   └─> Update memory (Redis + PostgreSQL)
   └─> Sync com CRM (se lead qualificado)
   └─> Log interaction

5. Return Response → User
```

### 2.3 Pontos de Falha Comuns

| Componente | Impacto se Falhar | Fallback |
|------------|-------------------|----------|
| Agent API Down | Sistema inoperante | Mensagem de manutenção |
| PostgreSQL Down | Sistema inoperante | Nenhum (crítico) |
| Redis Down | Performance degradada | Continua sem cache |
| LLM API Down | Sem respostas IA | Fallback para respostas pre-programadas |
| CRM API Down | Leads não sincronizam | Fila de retry + sync posterior |

**Referência Completa:** `/docs/arquitetura.md`

---

## 3. Operações Comuns

### 3.1 Start/Stop do Sistema

#### Iniciar Sistema (Production)

```bash
# 1. Verificar pré-requisitos
./scripts/preflight-check.sh

# 2. Iniciar dependências (se não gerenciadas)
sudo systemctl start postgresql
sudo systemctl start redis

# 3. Verificar status das dependências
sudo systemctl status postgresql
sudo systemctl status redis

# 4. Iniciar aplicação
# Opção A: systemd
sudo systemctl start agente-api

# Opção B: Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Opção C: Kubernetes
kubectl apply -f k8s/production/

# 5. Verificar saúde
curl https://api.example.com/health
# Esperado: {"status": "healthy", "version": "1.2.3"}

# 6. Verificar logs
sudo journalctl -u agente-api -f
# Ou
docker logs -f agente-api
# Ou
kubectl logs -f deployment/agente-api

# 7. Validar métricas
curl https://api.example.com/metrics | grep agent_requests_total
```

#### Parar Sistema (Gracefully)

```bash
# 1. Ativar modo manutenção (opcional)
./scripts/enable-maintenance-mode.sh
# Retorna 503 para novas requisições

# 2. Aguardar requisições em andamento finalizarem
# Verificar que não há requisições ativas
curl https://api.example.com/metrics | grep agent_active_requests
# Esperado: agent_active_requests 0

# 3. Parar aplicação
# Opção A: systemd
sudo systemctl stop agente-api

# Opção B: Docker
docker-compose -f docker-compose.prod.yml down

# Opção C: Kubernetes
kubectl scale deployment agente-api --replicas=0

# 4. Verificar que processo parou
ps aux | grep agente

# 5. Verificar logs para erros
tail -100 /var/log/agente/app.log
```

### 3.2 Deploy de Nova Versão

**Estratégia:** Canary Deployment (deploy gradual)

```bash
# 1. PRÉ-DEPLOY: Verificar checklist
# - [ ] Todos testes passando no CI
# - [ ] Coverage >= 80%
# - [ ] Security scan passou
# - [ ] Documentação atualizada
# - [ ] Changelog atualizado
# - [ ] Runbook revisado se necessário

# 2. Backup do banco de dados
./scripts/backup-database.sh
# Salvo em: /backups/db_YYYY-MM-DD_HH-MM.sql

# 3. Deploy Canary (5% tráfego)
./scripts/deploy-canary.sh v1.3.0 5%

# Ou manualmente no Kubernetes:
kubectl set image deployment/agente-api \
  agente-api=registry.example.com/agente-api:v1.3.0 \
  --record

kubectl patch deployment agente-api -p \
  '{"spec":{"replicas":1}}'  # 1 pod = ~5% do tráfego

# 4. MONITORAR por 2-4 horas
# Verificar dashboard: https://grafana.example.com/d/agent-overview
# Verificar métricas:
#   - Error rate < 1%
#   - Response time p95 < 2s
#   - No alertas críticos

# 5. Se estável, aumentar para 25%
kubectl scale deployment agente-api --replicas=3  # 25%
# Monitorar por 1-2h

# 6. Se estável, aumentar para 50%
kubectl scale deployment agente-api --replicas=6  # 50%
# Monitorar por 1h

# 7. Se estável, completar para 100%
kubectl scale deployment agente-api --replicas=12  # 100%

# 8. Remover versão antiga
kubectl delete deployment agente-api-old

# 9. Validação pós-deploy
./scripts/smoke-test.sh
# Testa endpoints críticos

# 10. Comunicar deploy completo
# Postar no Slack #deploys
```

**Se Algo Der Errado:**
```bash
# ROLLBACK IMEDIATO
kubectl rollout undo deployment/agente-api

# Ou para versão específica
kubectl rollout undo deployment/agente-api --to-revision=2

# Verificar rollback
kubectl rollout status deployment/agente-api

# Investigar causa
kubectl logs deployment/agente-api --previous
```

### 3.3 Rollback

```bash
# 1. Identificar versão para rollback
kubectl rollout history deployment/agente-api

# Output:
# REVISION  CHANGE-CAUSE
# 1         Deploy v1.2.0
# 2         Deploy v1.3.0 (current)
# 3         Deploy v1.3.1

# 2. Rollback para revisão específica
kubectl rollout undo deployment/agente-api --to-revision=1

# Ou rollback para versão anterior
kubectl rollout undo deployment/agente-api

# 3. Verificar rollback em progresso
kubectl rollout status deployment/agente-api
# Esperado: "deployment "agente-api" successfully rolled out"

# 4. Validar versão
curl https://api.example.com/version
# Esperado: {"version": "1.2.0"}

# 5. Validar funcionalidade
./scripts/smoke-test.sh

# 6. Monitorar métricas
# Verificar que error rate voltou ao normal

# 7. Comunicar rollback
# Postar no Slack + criar postmortem
```

### 3.4 Escalar Recursos

#### Scale Up (Vertical Scaling)

```bash
# Aumentar recursos de CPU/memória

# Kubernetes:
kubectl patch deployment agente-api -p \
  '{"spec":{"template":{"spec":{"containers":[{
    "name":"agente-api",
    "resources":{
      "requests":{"cpu":"2","memory":"4Gi"},
      "limits":{"cpu":"4","memory":"8Gi"}
    }
  }]}}}}'

# Docker Compose:
# Editar docker-compose.yml:
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 8G

# Reiniciar
docker-compose up -d
```

#### Scale Out (Horizontal Scaling)

```bash
# Aumentar número de instâncias

# Kubernetes:
kubectl scale deployment agente-api --replicas=20

# Verificar
kubectl get pods -l app=agente-api

# Auto-scaling (HPA)
kubectl autoscale deployment agente-api \
  --cpu-percent=70 \
  --min=5 \
  --max=50
```

### 3.5 Acessar Logs

```bash
# Logs em produção (últimos 100 linhas)
sudo journalctl -u agente-api -n 100

# Logs em tempo real
sudo journalctl -u agente-api -f

# Logs Docker
docker logs -f agente-api --tail 100

# Logs Kubernetes
kubectl logs -f deployment/agente-api

# Logs de pod específico
kubectl logs pod-name -c agente-api

# Logs de todos os pods
kubectl logs -l app=agente-api --all-containers

# Logs anteriores (se crashou)
kubectl logs pod-name --previous

# Filtrar logs (erro)
kubectl logs deployment/agente-api | grep ERROR

# Exportar logs para análise
kubectl logs deployment/agente-api --since=1h > logs_last_hour.txt
```

### 3.6 Acessar Banco de Dados

```bash
# PostgreSQL - Conectar
psql -h localhost -U agente_user -d agente_ia

# Queries úteis:

-- Ver conversas recentes
SELECT id, user_id, created_at, status
FROM conversations
ORDER BY created_at DESC
LIMIT 10;

-- Ver leads criados hoje
SELECT id, email, score, created_at
FROM leads
WHERE created_at >= CURRENT_DATE
ORDER BY score DESC;

-- Ver estatísticas
SELECT
  DATE(created_at) as date,
  COUNT(*) as total_conversations,
  AVG(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) * 100 as completion_rate
FROM conversations
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date;

-- Verificar tamanho do banco
SELECT pg_size_pretty(pg_database_size('agente_ia'));

-- Ver queries lentas
SELECT query, calls, mean_exec_time, max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

# Backup manual
pg_dump -h localhost -U agente_user agente_ia > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
psql -h localhost -U agente_user agente_ia < backup_20240120_153045.sql
```

### 3.7 Acessar Redis

```bash
# Conectar ao Redis
redis-cli -h localhost -p 6379

# Comandos úteis:

# Ver informações gerais
INFO

# Ver uso de memória
INFO memory

# Ver todas as keys (CUIDADO em produção!)
KEYS *

# Ver keys com padrão
KEYS conversation:*

# Ver valor de uma key
GET conversation:abc-123

# Ver TTL de uma key
TTL conversation:abc-123

# Deletar key
DEL conversation:abc-123

# Limpar cache (CUIDADO!)
FLUSHDB  # Limpa database atual
FLUSHALL # Limpa todas databases

# Monitorar comandos em tempo real
MONITOR

# Ver estatísticas
INFO stats

# Ver hit rate do cache
INFO stats | grep keyspace_hits
INFO stats | grep keyspace_misses
```

---

## 4. Procedimentos de Incidente

### 4.1 Processo Geral de Resposta

```
┌─────────────────────────────────────────────────────┐
│                 INCIDENTE DETECTADO                 │
│         (Alerta, Usuário, Monitoring)               │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│            1. ACKNOWLEDGE (< 5 min)                 │
│  - Confirmar recebimento do alerta                  │
│  - Postar no Slack #incidents                       │
│  - Iniciar timer                                    │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│            2. ASSESS (< 10 min)                     │
│  - Qual a severidade? (P0, P1, P2)                  │
│  - Quantos usuários afetados?                       │
│  - Sistema está up ou down?                         │
│  - Verificar dashboard e logs                       │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│            3. MITIGATE (< 30 min)                   │
│  - Aplicar solução temporária (workaround)          │
│  - Objetivo: restaurar serviço                      │
│  - Não precisa ser a solução final                  │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│            4. RESOLVE                               │
│  - Identificar root cause                           │
│  - Aplicar fix definitivo                           │
│  - Validar que problema foi resolvido               │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│            5. DOCUMENT                              │
│  - Atualizar incident ticket                        │
│  - Comunicar stakeholders                           │
│  - Agendar postmortem (se P0/P1)                    │
└─────────────────────────────────────────────────────┘
```

### 4.2 Severidade de Incidentes

| Prioridade | Descrição | Resposta | Exemplo |
|------------|-----------|----------|---------|
| **P0 - Crítico** | Sistema down ou degradação severa | 15 min | Sistema completamente inacessível |
| **P1 - Alto** | Funcionalidade importante afetada | 2 horas | Error rate >5%, integrações down |
| **P2 - Médio** | Problema menor, workaround existe | 1 dia útil | Performance degradada, logs faltando |
| **P3 - Baixo** | Problema cosmético ou menor | Best effort | Typo em mensagem, métrica faltando |

### 4.3 Comunicação Durante Incidentes

#### P0 - Crítico

```markdown
# Template de Comunicação P0

**Canal:** Slack #incidents + Email stakeholders

**Mensagem Inicial (< 5 min):**
🔥 INCIDENTE P0 - Sistema Down
- Detectado às: 14:32 BRT
- Impacto: Sistema completamente inacessível
- Investigando: @eng-oncall
- Status page: https://status.example.com
- Thread para updates: [link]

**Updates Regulares (a cada 15-30 min):**
🔄 UPDATE 14:45 - Investigação em andamento
- Root cause identificado: Database connection pool esgotado
- Ação em andamento: Aumentando pool size
- ETA: 15 minutos

**Resolução:**
✅ RESOLVIDO 15:10 - Sistema restaurado
- Duração: 38 minutos
- Root cause: Connection leak em código
- Fix aplicado: Rollback para v1.2.0
- Monitorando: Próximas 2 horas
- Postmortem: Agendado para amanhã 10h
```

#### P1 - Alto

```markdown
**Canal:** Slack #incidents

⚠️ INCIDENTE P1 - Error rate elevado
- Detectado às: 14:32 BRT
- Impacto: 10% dos requests falhando
- Investigando: @eng-oncall
- Updates: A cada 1h
```

### 4.4 Checklist de Resposta Rápida

Quando alerta chegar, execute na ordem:

```bash
# 1. ACKNOWLEDGE (1 min)
# - Confirmar alerta no PagerDuty
# - Postar no Slack: "Investigando incidente X"

# 2. VERIFICAR STATUS GERAL (2 min)
curl https://api.example.com/health
# Se retornar 200 OK: problema é intermitente
# Se retornar erro/timeout: sistema down

# 3. VERIFICAR DASHBOARD (2 min)
# Abrir: https://grafana.example.com/d/agent-overview
# Verificar:
# - Request rate (tráfego anormal?)
# - Error rate (spike de erros?)
# - Response time (latência alta?)
# - System resources (CPU/memória alta?)

# 4. VERIFICAR LOGS (3 min)
kubectl logs deployment/agente-api --tail=100 | grep ERROR
# Procurar por:
# - Stack traces
# - Erros de conexão (DB, Redis, LLM)
# - Timeouts
# - Exceções não tratadas

# 5. VERIFICAR DEPENDÊNCIAS (2 min)
# PostgreSQL
kubectl get pods -l app=postgresql  # Pods rodando?
# Redis
kubectl get pods -l app=redis       # Pods rodando?
# LLM API
curl https://api.openai.com/v1/models  # API respondendo?

# 6. DECISÃO RÁPIDA (<10 min total)
# - Se conseguiu identificar causa: Aplicar fix
# - Se não conseguiu: Escalar para senior engineer
# - Se sistema down: Considerar rollback
```

---

## 5. Guia de Troubleshooting

### 5.1 Árvore de Decisão - Sistema Down

```
Sistema não responde?
│
├─ API Gateway responde?
│  │
│  ├─ NÃO → Verificar Nginx/ALB
│  │        └─> Logs: /var/log/nginx/error.log
│  │        └─> Status: systemctl status nginx
│  │
│  └─ SIM → API responde?
│            │
│            ├─ NÃO → Verificar Agent API
│            │        └─> Pods: kubectl get pods
│            │        └─> Logs: kubectl logs deployment/agente-api
│            │        └─> Health: curl /health
│            │
│            └─ SIM → Problema intermitente
│                     └─> Ver Seção 5.3
```

### 5.2 Problemas Comuns e Soluções

#### Problema: "Sistema não responde" (HTTP 503/504)

**Diagnóstico:**
```bash
# 1. Verificar se pods estão rodando
kubectl get pods -l app=agente-api

# Se STATUS != Running:
kubectl describe pod POD_NAME

# 2. Verificar logs
kubectl logs deployment/agente-api --tail=50

# 3. Verificar recursos
kubectl top pods -l app=agente-api
```

**Soluções:**

```bash
# SOLUÇÃO 1: Restart pods (se OOM ou crash)
kubectl rollout restart deployment/agente-api

# SOLUÇÃO 2: Scale up (se CPU/memória alta)
kubectl scale deployment agente-api --replicas=20

# SOLUÇÃO 3: Verificar health das dependências
# PostgreSQL
kubectl exec -it postgres-pod -- psql -U user -c "SELECT 1"

# Redis
kubectl exec -it redis-pod -- redis-cli ping
```

#### Problema: "Error rate alto" (>5%)

**Diagnóstico:**
```bash
# 1. Ver erros nos logs
kubectl logs deployment/agente-api | grep ERROR | tail -50

# 2. Identificar padrão
# - Todos erros iguais? (problema específico)
# - Erros variados? (problema geral)

# 3. Verificar métricas
curl https://api.example.com/metrics | grep agent_errors
```

**Soluções por tipo de erro:**

```bash
# ERRO: "Database connection failed"
# → PostgreSQL down ou connection pool esgotado
# Verificar:
kubectl get pods -l app=postgresql
# Aumentar connection pool:
kubectl set env deployment/agente-api DB_POOL_SIZE=50

# ERRO: "Redis connection timeout"
# → Redis down ou rede lenta
kubectl get pods -l app=redis
kubectl logs deployment/redis

# ERRO: "LLM API rate limit"
# → Muitas chamadas ao LLM
# Verificar cache hit rate:
redis-cli INFO stats | grep keyspace_hits
# Aumentar cache se hit rate < 60%

# ERRO: "Timeout waiting for response"
# → LLM API lento
# Ver latência do LLM:
kubectl logs deployment/agente-api | grep "LLM latency"
# Considerar usar modelo mais rápido ou aumentar timeout
```

#### Problema: "Response time alto" (P95 >3s)

**Diagnóstico:**
```bash
# 1. Ver distribuição de latências
curl https://api.example.com/metrics | grep agent_response_time

# 2. Identificar gargalo com tracing
# Ver traces no Grafana Tempo ou similar

# 3. Verificar slow queries
kubectl exec -it postgres-pod -- psql -U user -d agente_ia -c \
  "SELECT query, mean_exec_time FROM pg_stat_statements
   ORDER BY mean_exec_time DESC LIMIT 10;"
```

**Soluções:**
```bash
# SOLUÇÃO 1: Otimizar queries lentas
# Adicionar índices se necessário

# SOLUÇÃO 2: Aumentar cache
# Verificar hit rate
redis-cli INFO stats | grep hit_rate

# SOLUÇÃO 3: Scale out
kubectl scale deployment agente-api --replicas=20

# SOLUÇÃO 4: Usar LLM mais rápido
# Editar config para usar gpt-3.5-turbo ao invés de gpt-4
kubectl set env deployment/agente-api DEFAULT_MODEL=gpt-3.5-turbo
```

#### Problema: "Integração com CRM falhando"

**Diagnóstico:**
```bash
# 1. Verificar logs de integração
kubectl logs deployment/agente-api | grep "CRM"

# 2. Testar API do CRM manualmente
curl -H "Authorization: Bearer $CRM_API_KEY" \
  https://api.salesforce.com/services/data/v57.0/

# 3. Verificar fila de retry
redis-cli LLEN crm_retry_queue
```

**Soluções:**
```bash
# SOLUÇÃO 1: CRM API temporariamente down
# → Verificar status do CRM
curl https://status.salesforce.com

# → Ativar fallback (fila de retry está ativa?)
kubectl logs deployment/agente-api | grep "fallback"

# SOLUÇÃO 2: API Key expirada
# → Regenerar API key no CRM
# → Atualizar secret no Kubernetes
kubectl create secret generic crm-credentials \
  --from-literal=api-key=NEW_KEY \
  --dry-run=client -o yaml | kubectl apply -f -

# → Restart para pegar novo secret
kubectl rollout restart deployment/agente-api

# SOLUÇÃO 3: Rate limit do CRM
# → Adicionar rate limiting no client
# → Aumentar intervalo entre retries
```

#### Problema: "Alto uso de memória" (>85%)

**Diagnóstico:**
```bash
# 1. Ver uso atual
kubectl top pods -l app=agente-api

# 2. Ver histórico
# Abrir Grafana: https://grafana.example.com
# Dashboard: Agent API - Resources

# 3. Identificar memory leak (se uso crescente)
kubectl logs deployment/agente-api | grep "memory"
```

**Soluções:**
```bash
# SOLUÇÃO IMEDIATA: Restart pods
kubectl rollout restart deployment/agente-api

# SOLUÇÃO 1: Aumentar memória disponível
kubectl patch deployment agente-api -p \
  '{"spec":{"template":{"spec":{"containers":[{
    "name":"agente-api",
    "resources":{"limits":{"memory":"8Gi"}}
  }]}}}}'

# SOLUÇÃO 2: Otimizar código
# - Limitar tamanho de cache em memória
# - Limpar objetos não usados
# - Usar generators ao invés de listas

# SOLUÇÃO 3: Investigar leak
# Adicionar memory profiling temporariamente
kubectl set env deployment/agente-api MEMORY_PROFILING=true
# Analisar profile depois
```

### 5.3 Problemas Intermitentes

**Sintoma:** Alguns requests falham, outros funcionam

**Diagnóstico:**
```bash
# 1. Verificar se é problema de load balancing
# Ver distribuição de erros por pod
kubectl logs -l app=agente-api --prefix=true | grep ERROR

# 2. Ver se algum pod específico tem problemas
kubectl get pods -l app=agente-api
kubectl logs POD_NAME | grep ERROR

# 3. Verificar rate limiting
curl https://api.example.com/metrics | grep rate_limit_exceeded

# 4. Verificar timeouts
curl https://api.example.com/metrics | grep timeout
```

**Soluções:**
```bash
# SOLUÇÃO 1: Pod específico com problema
# Identificar pod problemático
kubectl logs POD_NAME | grep ERROR | wc -l

# Deletar pod problemático (será recriado)
kubectl delete pod POD_NAME

# SOLUÇÃO 2: Rate limiting muito agressivo
# Aumentar limites
kubectl set env deployment/agente-api \
  RATE_LIMIT_PER_MINUTE=200

# SOLUÇÃO 3: Timeout muito baixo
kubectl set env deployment/agente-api \
  REQUEST_TIMEOUT=30
```

### 5.4 Comandos de Diagnóstico Rápido

```bash
# HEALTH CHECK completo
./scripts/health-check.sh

# Ou manualmente:
curl https://api.example.com/health          # API health
curl https://api.example.com/health/db       # Database health
curl https://api.example.com/health/redis    # Redis health
curl https://api.example.com/health/llm      # LLM API health

# MÉTRICAS principais
curl https://api.example.com/metrics | grep -E "(agent_requests_total|agent_errors_total|agent_response_time)"

# LOGS com contexto
kubectl logs deployment/agente-api --tail=100 | grep -B 3 -A 3 ERROR

# TOP consumers de recursos
kubectl top pods --sort-by=memory
kubectl top pods --sort-by=cpu

# REDE - Verificar conectividade
kubectl exec -it POD_NAME -- curl -v https://api.openai.com
kubectl exec -it POD_NAME -- nc -zv postgres-service 5432
kubectl exec -it POD_NAME -- nc -zv redis-service 6379
```

**Referência Completa:** `/docs/guias/troubleshooting.md`

---

## 6. Monitoramento e Alertas

### 6.1 Dashboards Principais

#### Dashboard: Agent Overview
**URL:** `https://grafana.example.com/d/agent-overview`

**Painéis principais:**
- Request Rate (requisições/min)
- Error Rate (%)
- Response Time (p50, p95, p99)
- Active Users
- System Resources (CPU, memória)

**Como interpretar:**
```
Request Rate spike?
└─> Tráfego legítimo ou ataque? Verificar User-Agents

Error Rate >1%?
└─> Ver logs: kubectl logs deployment/agente-api | grep ERROR

Response Time p95 >2s?
└─> Verificar:
    - LLM latency
    - Database slow queries
    - Cache hit rate
```

#### Dashboard: Business Metrics
**URL:** `https://grafana.example.com/d/agent-business`

**Painéis principais:**
- Conversions (leads/dia)
- CSAT Score
- Engagement Rate
- Handoff Rate

#### Dashboard: LLM Usage
**URL:** `https://grafana.example.com/d/agent-llm`

**Painéis principais:**
- Token Usage (input/output)
- Cost per Day
- Model Distribution
- Intent Accuracy

### 6.2 Alertas Críticos (P0)

| Alerta | Threshold | Ação Imediata |
|--------|-----------|---------------|
| **SystemDown** | up==0 por 1 min | Verificar pods, verificar logs, considerar restart |
| **HighErrorRate** | Error rate >10% por 5 min | Ver logs, identificar erro, rollback se necessário |
| **DatabaseDown** | pg_up==0 por 1 min | Verificar PostgreSQL, verificar rede, escalar para DBA |
| **RedisDown** | redis_up==0 por 1 min | Verificar Redis, sistema continua mas sem cache |
| **HighResponseTime** | p99 >10s por 10 min | Ver LLM latency, DB queries, considerar scale out |

### 6.3 Alertas Altos (P1)

| Alerta | Threshold | Ação (2h) |
|--------|-----------|-----------|
| **HighResponseTimeP95** | p95 >3s por 15 min | Investigar gargalos, otimizar queries |
| **ElevatedErrorRate** | Error rate 5-10% por 10 min | Identificar padrão de erros |
| **LowIntentAccuracy** | Accuracy <85% por 1h | Revisar prompts, analisar conversas |
| **HighMemoryUsage** | Memória >85% por 10 min | Verificar leaks, considerar scale up |

### 6.4 Como Responder a Alertas

```bash
# QUANDO ALERTA CHEGAR:

# 1. Acknowledge no PagerDuty (< 1 min)
# Confirmar recebimento

# 2. Abrir Dashboard relevante (< 2 min)
# Ex: SystemDown → Dashboard Agent Overview

# 3. Verificar logs (< 3 min)
kubectl logs deployment/agente-api --tail=100 | grep ERROR

# 4. Avaliar severidade (< 5 min)
# - Sistema down? → P0
# - Funcionalidade afetada? → P1
# - Performance degradada? → P1/P2

# 5. Aplicar fix ou escalar (< 15 min para P0)
# Ver seção específica do alerta em:
# /templates/monitoramento/alertas.yaml

# 6. Atualizar stakeholders
# Postar no Slack #incidents

# 7. Resolver alerta
# Silenciar no Prometheus/AlertManager quando resolvido
```

**Referência Completa:** `/templates/monitoramento/alertas.yaml`

---

## 7. Tarefas de Manutenção

### 7.1 Diárias

```bash
# Executar a cada manhã (9h)

# 1. Verificar saúde do sistema
./scripts/daily-health-check.sh

# Ou manualmente:
# - Abrir dashboard Agent Overview
# - Verificar error rate < 0.5%
# - Verificar response time p95 < 2s
# - Verificar uptime >= 99.5%

# 2. Revisar alertas das últimas 24h
# Ver: https://alertmanager.example.com

# 3. Verificar custos
curl https://api.example.com/metrics | grep cost_usd_total
# Comparar com budget diário (target: <$400)

# 4. Revisar top erros
kubectl logs deployment/agente-api --since=24h | grep ERROR | sort | uniq -c | sort -rn | head -10

# 5. Verificar espaço em disco
kubectl exec -it POD_NAME -- df -h
# Alerta se >80%
```

### 7.2 Semanais

```bash
# Executar toda segunda-feira

# 1. Review de métricas de negócio
# - Conversion rate
# - CSAT score
# - Handoff rate
# - Intent accuracy
# Ver: https://grafana.example.com/d/agent-business

# 2. Backup verification
# Verificar que backups diários estão sendo feitos
ls -lh /backups/db_* | tail -7

# Testar restore de backup mais recente (em staging)
./scripts/test-backup-restore.sh

# 3. Atualizar dependências
# Verificar atualizações de segurança
pip list --outdated
npm outdated  # Se houver frontend

# 4. Revisar logs de segurança
kubectl logs deployment/agente-api --since=7d | grep -E "(injection|unauthorized|suspicious)"

# 5. Limpar dados antigos
# Conversas >90 dias
psql -d agente_ia -c "DELETE FROM conversations WHERE created_at < NOW() - INTERVAL '90 days';"

# Logs >30 dias
find /var/log/agente -name "*.log" -mtime +30 -delete
```

### 7.3 Mensais

```bash
# Executar primeiro dia do mês

# 1. Review de capacidade
# - Uso médio de CPU/memória
# - Crescimento de tráfego
# - Necessidade de scale up/out
# Decisão: Ajustar recursos se necessário

# 2. Review de custos
# - Total gasto no mês (LLM + infra)
# - Custo por conversa
# - ROI do projeto
# Relatório para stakeholders

# 3. Update de documentação
# - Runbook (este arquivo)
# - Arquitetura
# - Processos
# Verificar se está atualizado

# 4. Disaster recovery drill
# Simular falha e testar procedimento de recovery
./scripts/dr-drill.sh

# 5. Security audit
# - Revisar API keys (rotar se necessário)
# - Revisar permissões
# - Scan de vulnerabilidades
./scripts/security-scan.sh

# 6. Performance tuning
# - Identificar queries lentas
# - Adicionar índices se necessário
# - Otimizar prompts
```

### 7.4 Trimestrais

```bash
# 1. Revisão de arquitetura
# - Avaliar tech debt
# - Planejar melhorias
# - Atualizar roadmap

# 2. Load testing
# Verificar que sistema aguenta tráfego esperado
./scripts/load-test.sh

# 3. Update de versões maiores
# - Python
# - PostgreSQL
# - Redis
# Planejar em ambiente de staging primeiro

# 4. Treinamento do time
# - Novo membros: Runbook walkthrough
# - Time todo: Simulação de incidentes
```

---

## 8. Procedimentos de Emergência

### 8.1 Sistema Completamente Down

**OBJETIVO:** Restaurar serviço o mais rápido possível

```bash
# PASSO 1: Avaliar situação (2 min)
curl https://api.example.com/health
# Não responde? Sistema down.

# PASSO 2: Verificar pods (1 min)
kubectl get pods -l app=agente-api
# Todos em CrashLoopBackOff? Problema grave.

# PASSO 3: Ver logs (2 min)
kubectl logs deployment/agente-api --tail=50
# Identificar erro crítico

# PASSO 4: DECISÃO RÁPIDA (<5 min total)

# OPÇÃO A: Erro conhecido? Aplicar fix conhecido
# Ex: Config errada
kubectl set env deployment/agente-api VARIABLE=correct_value
kubectl rollout restart deployment/agente-api

# OPÇÃO B: Problema de recurso? Scale up
kubectl scale deployment agente-api --replicas=20

# OPÇÃO C: Não sabe a causa? ROLLBACK
kubectl rollout undo deployment/agente-api

# OPÇÃO D: Rollback não funciona? Usar versão estável conhecida
kubectl set image deployment/agente-api \
  agente-api=registry.example.com/agente-api:v1.2.0-stable

# PASSO 5: Verificar restauração (3 min)
watch -n 5 'curl -s https://api.example.com/health || echo "Still down"'

# PASSO 6: Comunicar (2 min)
# Postar no Slack #incidents:
# "Sistema restaurado. Duração: X minutos. Investigando root cause."

# PASSO 7: Monitorar (30 min)
# Verificar dashboard que métricas voltaram ao normal

# PASSO 8: Post-incident
# Agendar postmortem
# Documentar timeline
# Identificar ações corretivas
```

### 8.2 Database Irrecuperável

**CENÁRIO:** PostgreSQL corrompido, não inicia

```bash
# PASSO 1: Avaliar dano
kubectl logs pod/postgresql-0

# PASSO 2: Tentar restart
kubectl delete pod postgresql-0
# Aguardar pod recriar e ver se inicia

# PASSO 3: Se não funcionar, RESTORE de backup

# 3.1. Criar novo database vazio
kubectl exec -it postgresql-0 -- createdb agente_ia_new

# 3.2. Restaurar último backup
kubectl cp /backups/latest.sql postgresql-0:/tmp/backup.sql
kubectl exec -it postgresql-0 -- \
  psql agente_ia_new < /tmp/backup.sql

# 3.3. Verificar integridade
kubectl exec -it postgresql-0 -- \
  psql agente_ia_new -c "SELECT COUNT(*) FROM conversations;"

# 3.4. Apontar aplicação para novo database
kubectl set env deployment/agente-api \
  DATABASE_NAME=agente_ia_new

# 3.5. Restart aplicação
kubectl rollout restart deployment/agente-api

# PASSO 4: Comunicar perda de dados (se houver)
# "Restaurado a partir de backup de [timestamp]"
# "Dados entre [X] e [Y] foram perdidos"

# PASSO 5: RCA - Root Cause Analysis
# - O que causou corrupção?
# - Como prevenir?
# - Atualizar runbook
```

### 8.3 Ataque DDoS em Andamento

**SINTOMAS:**
- Request rate 10x acima do normal
- Erro rate alto
- Response time altíssimo
- Alertas de rate limiting

```bash
# PASSO 1: Confirmar ataque (3 min)
# Ver dashboard
# Request rate anormal? De quais IPs?

# Ver logs
kubectl logs deployment/agente-api | grep rate_limit_exceeded

# Ver top IPs
kubectl logs deployment/agente-api | grep -oE '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | sort | uniq -c | sort -rn | head -20

# PASSO 2: Mitigar IMEDIATAMENTE (<10 min)

# 2.1. Bloquear IPs atacantes no API Gateway
# Nginx:
sudo nano /etc/nginx/conf.d/blacklist.conf
# Adicionar:
deny 1.2.3.4;
deny 5.6.7.8;

sudo nginx -t && sudo systemctl reload nginx

# Ou via cloud provider (melhor)
# AWS WAF:
aws wafv2 update-ip-set \
  --id IP_SET_ID \
  --addresses 1.2.3.4/32 5.6.7.8/32

# 2.2. Reduzir rate limits temporariamente
kubectl set env deployment/agente-api \
  RATE_LIMIT_PER_MINUTE=10  # Muito restritivo

# 2.3. Ativar modo manutenção parcial
# Bloquear novos usuários, manter usuários autenticados
kubectl set env deployment/agente-api \
  MAINTENANCE_MODE=partial

# PASSO 3: Escalar recursos se sistema ainda está respondendo
kubectl scale deployment agente-api --replicas=50

# PASSO 4: Habilitar CDN/DDoS protection
# Cloudflare, AWS Shield, etc

# PASSO 5: Comunicar
# Postar no Slack #incidents + #security

# PASSO 6: Monitorar
# Verificar que ataque foi mitigado
# Request rate voltou ao normal?

# PASSO 7: Post-incident
# - Documentar IPs atacantes
# - Melhorar defesas
# - Considerar Cloudflare/AWS Shield permanentemente
```

### 8.4 Data Breach Suspeito

**SINTOMAS:**
- Acessos não autorizados
- Dados sensíveis vazados
- Atividade suspeita nos logs

```bash
# PASSO 1: ISOLAR IMEDIATAMENTE
# Desconectar sistema de integrações
kubectl set env deployment/agente-api \
  ENABLE_INTEGRATIONS=false

# PASSO 2: Coletar evidências
# NÃO deletar logs!
# Copiar todos logs para análise forense
kubectl logs deployment/agente-api --all-containers --since=24h > incident_logs_$(date +%Y%m%d).txt

# Copiar logs do API Gateway
sudo cp -r /var/log/nginx/access.log /tmp/incident_logs/

# PASSO 3: Notificar IMEDIATAMENTE
# - CISO/Security team
# - Legal
# - DPO (LGPD)

# PASSO 4: Avaliar extensão
# - Quais dados foram acessados?
# - Quais usuários foram afetados?
# - Como acesso foi obtido?

# PASSO 5: Conter
# - Resetar todas API keys
# - Forçar logout de todos usuários
# - Revogar tokens comprometidos

# PASSO 6: NÃO RESTAURAR até investigação completa
# Sistema fica offline até OK do security team

# PASSO 7: Seguir plano de resposta a incidentes de segurança
# Ver: /docs/seguranca/incident-response-plan.md
```

### 8.5 LLM Provider Completamente Down

**CENÁRIO:** OpenAI/Anthropic API inacessível

```bash
# PASSO 1: Confirmar que é problema deles
curl https://status.openai.com
# Ou https://status.anthropic.com

# PASSO 2: Ativar fallback IMEDIATAMENTE

# Opção A: Usar provider alternativo
kubectl set env deployment/agente-api \
  LLM_PROVIDER=anthropic  # Se OpenAI down

# Opção B: Usar respostas pre-programadas
kubectl set env deployment/agente-api \
  FALLBACK_MODE=true

# PASSO 3: Comunicar usuários
# "Estamos com instabilidade temporária. Respostas podem ser limitadas."

# PASSO 4: Monitorar status do provider
# Aguardar volta

# PASSO 5: Quando voltar, desativar fallback
kubectl set env deployment/agente-api \
  LLM_PROVIDER=openai \
  FALLBACK_MODE=false

# PASSO 6: Post-incident
# - Considerar multi-provider strategy permanente
# - Melhorar fallbacks
```

---

## 9. Escalação

### 9.1 Quando Escalar?

**Escalar IMEDIATAMENTE se:**
- Sistema down por >15 minutos e você não sabe resolver
- Suspeita de security breach
- Data loss
- Não consegue mitigar incidente P0 em 30 minutos

**Escalar em 2h se:**
- Incidente P1 sem progresso
- Problema complexo que requer expertise específica
- Múltiplos problemas simultâneos

### 9.2 Cadeia de Escalação

```
┌─────────────────────────────────────────────┐
│  Nível 1: Engineer On-Call                  │
│  - Responde a alertas                       │
│  - Aplica runbooks                          │
│  - Resolve incidentes simples               │
│  Contato: @oncall no Slack                  │
└──────────────┬──────────────────────────────┘
               │ Escalar após 30min sem resolução
               ▼
┌─────────────────────────────────────────────┐
│  Nível 2: Senior Engineer / Tech Lead       │
│  - Problemas complexos                      │
│  - Decisões arquiteturais                   │
│  - Coordena resposta a incidentes           │
│  Contato: +55 11 99999-1234 (Tech Lead)     │
└──────────────┬──────────────────────────────┘
               │ Escalar se impacto crítico ou >1h
               ▼
┌─────────────────────────────────────────────┐
│  Nível 3: Engineering Manager / CTO         │
│  - Incidentes que afetam negócio            │
│  - Decisões de budget/recursos              │
│  - Comunicação com stakeholders C-level     │
│  Contato: +55 11 99999-5678 (CTO)           │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  LATERAL: Especialistas                     │
│  - DBA: Problemas de database               │
│  - Security: Suspeita de breach             │
│  - ML Engineer: Problemas de prompts/LLM    │
│  - DevOps: Problemas de infra               │
└─────────────────────────────────────────────┘
```

### 9.3 Informações para Incluir na Escalação

```markdown
**Template de Escalação**

🚨 ESCALANDO INCIDENTE

**Prioridade:** P0 / P1 / P2
**Início:** 14:32 BRT
**Duração até agora:** 45 minutos

**Resumo:**
Sistema apresentando error rate de 15%. Tentei X, Y, Z sem sucesso.

**Impacto:**
- 500 usuários afetados
- Conversões paradas
- Revenue impact: ~R$ 5k/hora

**O que já tentei:**
1. Restart dos pods - Não funcionou
2. Rollback para v1.2.0 - Ainda com erros
3. Verificado DB/Redis - Ambos OK

**Logs/Evidências:**
[Anexar logs relevantes]

**Dashboard:**
https://grafana.example.com/d/agent-overview

**Preciso de ajuda com:**
Root cause não identificado, erro intermitente.

**Próximos passos se não houver resposta em 15min:**
Vou colocar sistema em manutenção.

cc: @tech-lead @senior-engineer
```

---

## 10. Runbooks Específicos

### 10.1 Runbook: Carga Alta (Traffic Spike)

**Sintomas:**
- Request rate 3x-5x acima do normal
- Response time aumentando
- CPU/memória alta

**Diagnóstico:**
```bash
# 1. Ver tráfego atual vs histórico
# Dashboard Grafana: Request rate panel

# 2. Verificar se é tráfego legítimo
kubectl logs deployment/agente-api | grep User-Agent | sort | uniq -c

# 3. Verificar recursos
kubectl top pods -l app=agente-api
```

**Resposta:**
```bash
# SE TRÁFEGO LEGÍTIMO (evento, marketing, etc):

# 1. Scale out imediatamente
kubectl scale deployment agente-api --replicas=30

# 2. Verificar que novos pods estão saudáveis
kubectl get pods -l app=agente-api
# Aguardar todos STATUS = Running

# 3. Monitorar métricas
# Response time deve voltar ao normal em 2-5 min

# 4. Ativar auto-scaling se ainda não ativo
kubectl autoscale deployment agente-api \
  --cpu-percent=70 --min=10 --max=50

# SE TRÁFEGO MALICIOSO (ver Seção 8.3 - DDoS)
```

### 10.2 Runbook: Database Issues

**Sintomas:**
- Erros "database connection failed"
- Queries lentas
- Connection pool exhausted

**Diagnóstico:**
```bash
# 1. Verificar se database está up
kubectl get pods -l app=postgresql

# 2. Verificar conexões ativas
kubectl exec -it postgres-pod -- psql -U user -d agente_ia -c \
  "SELECT count(*) FROM pg_stat_activity;"

# 3. Ver queries lentas em andamento
kubectl exec -it postgres-pod -- psql -U user -d agente_ia -c \
  "SELECT pid, now() - query_start as duration, query
   FROM pg_stat_activity
   WHERE state = 'active'
   ORDER BY duration DESC;"

# 4. Verificar espaço em disco
kubectl exec -it postgres-pod -- df -h
```

**Resposta:**
```bash
# PROBLEMA: Connection pool exhausted

# Solução temporária: Aumentar pool size
kubectl set env deployment/agente-api \
  DB_POOL_SIZE=50 \
  DB_MAX_OVERFLOW=20

kubectl rollout restart deployment/agente-api

# Solução permanente: Investigar connection leaks


# PROBLEMA: Queries lentas

# 1. Identificar query problemática (já executado acima)

# 2. Matar query se necessário
kubectl exec -it postgres-pod -- psql -U user -d agente_ia -c \
  "SELECT pg_terminate_backend(PID);"

# 3. Adicionar índice se necessário
kubectl exec -it postgres-pod -- psql -U user -d agente_ia -c \
  "CREATE INDEX CONCURRENTLY idx_conversations_user_id ON conversations(user_id);"

# 4. Atualizar estatísticas
kubectl exec -it postgres-pod -- psql -U user -d agente_ia -c \
  "ANALYZE;"


# PROBLEMA: Espaço em disco cheio (>90%)

# 1. Limpar dados antigos
kubectl exec -it postgres-pod -- psql -U user -d agente_ia -c \
  "DELETE FROM conversations WHERE created_at < NOW() - INTERVAL '90 days';"

# 2. Vacuum
kubectl exec -it postgres-pod -- psql -U user -d agente_ia -c \
  "VACUUM FULL;"

# 3. Aumentar disco (se necessário)
# Depende do provider (AWS EBS, GCP PD, etc)
```

### 10.3 Runbook: LLM Issues

**Sintomas:**
- Rate limit errors
- High latency (>10s)
- Custos disparados

**Diagnóstico:**
```bash
# 1. Ver erros de LLM nos logs
kubectl logs deployment/agente-api | grep "LLM" | grep ERROR

# 2. Ver métricas de uso
curl https://api.example.com/metrics | grep llm_

# 3. Ver latência do LLM
kubectl logs deployment/agente-api | grep "LLM latency" | tail -20

# 4. Ver custos
curl https://api.example.com/metrics | grep cost_usd
```

**Resposta:**
```bash
# PROBLEMA: Rate limit exceeded

# Solução 1: Aumentar cache agressivamente
kubectl set env deployment/agente-api \
  CACHE_TTL=3600  # 1 hora

# Solução 2: Usar tier maior da API (se disponível)
# Ou espaçar requests com rate limiter


# PROBLEMA: High latency

# Solução 1: Usar modelo mais rápido
kubectl set env deployment/agente-api \
  DEFAULT_MODEL=gpt-3.5-turbo  # Mais rápido que gpt-4

# Solução 2: Reduzir max_tokens
kubectl set env deployment/agente-api \
  MAX_TOKENS=300

# Solução 3: Implementar timeout
kubectl set env deployment/agente-api \
  LLM_TIMEOUT=10


# PROBLEMA: Custos muito altos

# 1. Ver distribuição de uso por modelo
curl https://api.example.com/metrics | grep llm_tokens_by_model

# 2. Ações imediatas:
# - Aumentar cache (reduz chamadas)
kubectl set env deployment/agente-api CACHE_TTL=3600

# - Usar modelo mais barato para queries simples
kubectl set env deployment/agente-api \
  SIMPLE_QUERY_MODEL=gpt-3.5-turbo

# - Reduzir max_tokens
kubectl set env deployment/agente-api MAX_TOKENS=300

# - Otimizar prompts (menos tokens no input)

# 3. Análise mais profunda:
# - Quais conversas estão consumindo mais?
# - Há conversas muito longas?
# - Prompts muito grandes?
```

### 10.4 Runbook: Integração CRM Down

**Sintomas:**
- Erros "CRM API failed"
- Leads não sendo criados
- Fila de retry crescendo

**Diagnóstico:**
```bash
# 1. Ver logs de integração
kubectl logs deployment/agente-api | grep CRM

# 2. Testar API do CRM diretamente
curl -H "Authorization: Bearer $CRM_API_KEY" \
  https://api.salesforce.com/services/data/v57.0/

# 3. Ver status do CRM
curl https://status.salesforce.com

# 4. Ver tamanho da fila de retry
redis-cli LLEN crm_retry_queue
```

**Resposta:**
```bash
# SE CRM ESTÁ DOWN (problema deles):

# 1. Verificar que fallback está ativo
kubectl logs deployment/agente-api | grep "CRM fallback active"
# Deve ver: "CRM unavailable, queuing for retry"

# 2. Monitorar fila de retry
watch -n 30 'redis-cli LLEN crm_retry_queue'

# 3. Quando CRM voltar, processar fila
# Fila será processada automaticamente
# Ou force processamento:
kubectl exec -it agente-api-pod -- python scripts/process_retry_queue.py

# 4. Verificar que leads foram sincronizados
# Ver logs para confirmações


# SE CRM ESTÁ UP mas integração falhando:

# 1. Verificar API key
kubectl get secret crm-credentials -o jsonpath='{.data.api-key}' | base64 -d

# 2. Testar manualmente com essa key
curl -H "Authorization: Bearer $API_KEY" \
  https://api.salesforce.com/services/data/v57.0/

# 3. Se key expirada, regenerar e atualizar
kubectl create secret generic crm-credentials \
  --from-literal=api-key=NEW_KEY \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl rollout restart deployment/agente-api

# 4. Se problema de formato de dados, verificar logs
kubectl logs deployment/agente-api | grep "CRM request"
# Verificar formato do payload
```

### 10.5 Runbook: Deploy Falhou

**Sintomas:**
- Pods em CrashLoopBackOff após deploy
- Error rate disparou após deploy
- Nova versão não está funcionando

**Resposta:**
```bash
# AÇÃO IMEDIATA: ROLLBACK

# 1. Rollback (< 2 min)
kubectl rollout undo deployment/agente-api

# 2. Verificar que rollback completou
kubectl rollout status deployment/agente-api

# 3. Verificar que sistema voltou ao normal
curl https://api.example.com/health
# Ver dashboard de métricas

# 4. Comunicar
# Postar no Slack: "Deploy v1.3.0 falhou, rollback executado"

# 5. INVESTIGAR causa

# Ver logs da versão que falhou
kubectl logs deployment/agente-api --previous

# Erros comuns:
# - Config errada (variável de ambiente faltando)
# - Migração de DB não rodou
# - Dependência quebrada
# - Bug no código

# 6. CORRIGIR e tentar novamente

# Se config errada:
# - Corrigir configmap/secret
# - Deploy novamente

# Se bug no código:
# - Fix do bug
# - Novo deploy (com mais cuidado)

# Se migração de DB:
# - Rodar migração manualmente
# - Deploy novamente
```

---

## 11. Checklist de On-Call

### 11.1 Início do Turno On-Call

```markdown
- [ ] Verificar que estou recebendo alertas (teste no PagerDuty)
- [ ] Ler resumo do turno anterior (handoff notes)
- [ ] Ver incidentes abertos ou em andamento
- [ ] Verificar saúde geral do sistema (dashboard)
- [ ] Verificar alertas ativos (mesmo que não críticos)
- [ ] Ter acesso VPN/SSH/kubectl configurado e testado
- [ ] Ter runbook (este documento) aberto e revisado
- [ ] Verificar calendário (algum deploy agendado?)
- [ ] Laptop carregado, internet estável
```

### 11.2 Durante o Turno

```markdown
- [ ] Checar dashboard 2-3x por dia
- [ ] Responder alertas em <15 min (P0) ou <2h (P1)
- [ ] Documentar ações tomadas
- [ ] Comunicar no Slack quando resolver incidentes
- [ ] Escalar se necessário (não hesite!)
- [ ] Manter laptop/celular próximo
```

### 11.3 Fim do Turno On-Call

```markdown
- [ ] Escrever handoff notes para próximo on-call
- [ ] Mencionar incidentes ativos ou problemas em andamento
- [ ] Mencionar tarefas que ficaram pendentes
- [ ] Transferir PagerDuty para próximo on-call
- [ ] Postar no Slack que turno terminou
```

### 11.4 Handoff Template

```markdown
**On-Call Handoff - [Data]**

**De:** @engineer-saindo
**Para:** @engineer-entrando

**Status Geral:** ✅ Estável / ⚠️ Issues menores / 🔥 Incidente ativo

**Incidentes nas últimas 24h:**
- 14:30 - Error rate spike (P1) - Resolvido com rollback
- 18:45 - Redis down (P0) - Resolvido com restart

**Problemas em andamento:**
- Nenhum / Integração com CRM intermitente, monitorando

**Alertas ativos (não críticos):**
- HighCacheHitRate - Normal, aguardando

**Manutenções planejadas:**
- Amanhã 3am - Manutenção do PostgreSQL (5 min downtime)

**Observações:**
- Traffic 20% acima do normal devido a campanha de marketing
- Cache hit rate melhorou após ajustes

**Contatos úteis:**
- DBA de plantão: @dba-oncall
- CTO: +55 11 99999-5678 (emergências)

**Documentos importantes:**
- Runbook: /docs/operacao/runbook.md
- Dashboard: https://grafana.example.com/d/agent-overview
```

---

## 12. Contatos e Recursos

### 12.1 Contatos de Emergência

| Função | Nome | Contato | Quando Usar |
|--------|------|---------|-------------|
| **On-Call Engineer** | Rotativo | @oncall no Slack | Primeira linha de resposta |
| **Tech Lead** | [NOME] | +55 11 99999-1234 | Incidentes P0 sem resolução em 30min |
| **Engineering Manager** | [NOME] | +55 11 99999-2345 | Decisões de budget/recursos |
| **CTO** | [NOME] | +55 11 99999-5678 | Incidentes críticos de negócio |
| **DBA** | [NOME] | +55 11 99999-3456 | Problemas de database |
| **Security Lead** | [NOME] | +55 11 99999-4567 | Suspeita de breach |
| **DevOps Lead** | [NOME] | +55 11 99999-6789 | Problemas de infraestrutura |

### 12.2 Canais de Comunicação

| Canal | Uso | Urgência |
|-------|-----|----------|
| **#incidents** | Incidentes ativos P0/P1 | URGENTE |
| **#alerts** | Todos os alertas (P0/P1/P2) | NORMAL |
| **#deploys** | Comunicação de deploys | NORMAL |
| **#engineering** | Discussões técnicas | NORMAL |
| **PagerDuty** | Alertas P0 (24/7) | CRÍTICO |

### 12.3 URLs Importantes

```markdown
**Production:**
- API: https://api.example.com
- Health: https://api.example.com/health
- Metrics: https://api.example.com/metrics
- Status Page: https://status.example.com

**Monitoring:**
- Grafana: https://grafana.example.com
  - Dashboard Principal: /d/agent-overview
  - Dashboard Negócio: /d/agent-business
  - Dashboard LLM: /d/agent-llm
- Prometheus: https://prometheus.example.com
- AlertManager: https://alertmanager.example.com

**Logs:**
- Kibana: https://kibana.example.com
- Datadog: https://app.datadoghq.com

**CI/CD:**
- GitHub Actions: https://github.com/company/agent-ia/actions
- ArgoCD: https://argocd.example.com

**Infrastructure:**
- AWS Console: https://console.aws.amazon.com
- Kubernetes Dashboard: https://k8s.example.com

**Documentation:**
- Internal Wiki: https://wiki.example.com
- Runbook (este doc): /docs/operacao/runbook.md
- Architecture: /docs/arquitetura.md
```

### 12.4 Credenciais e Acessos

```markdown
**Localização de Secrets:**

- **Kubernetes Secrets:**
  kubectl get secrets -n production

- **AWS Secrets Manager:**
  aws secretsmanager list-secrets --region us-east-1

- **Senha Master (1Password/LastPass):**
  Solicitar ao Tech Lead

**Acessos Necessários:**
- [ ] VPN corporativa
- [ ] kubectl configurado (production)
- [ ] AWS CLI configurado
- [ ] Acesso SSH aos servidores (se aplicável)
- [ ] PagerDuty account
- [ ] Grafana account
- [ ] GitHub (repository access)
- [ ] Slack (canais relevantes)
```

### 12.5 Ferramentas Essenciais

```bash
# Instalar ferramentas necessárias:

# kubectl (Kubernetes CLI)
brew install kubectl

# AWS CLI
brew install awscli

# PostgreSQL client
brew install postgresql

# Redis client
brew install redis

# jq (JSON parser)
brew install jq

# Verificar instalação
kubectl version --client
aws --version
psql --version
redis-cli --version
jq --version
```

### 12.6 Documentação de Referência

```markdown
**Documentação Interna:**
- Arquitetura: /docs/arquitetura.md
- Guias: /docs/guias/
- Processos: /docs/processos/
- Troubleshooting: /docs/guias/troubleshooting.md
- Metodologia: /docs/metodologia/OVERVIEW.md

**Documentação Externa:**
- Kubernetes: https://kubernetes.io/docs/
- PostgreSQL: https://www.postgresql.org/docs/
- Redis: https://redis.io/documentation
- FastAPI: https://fastapi.tiangolo.com/
- OpenAI API: https://platform.openai.com/docs/
- Prometheus: https://prometheus.io/docs/

**Runbooks Relacionados:**
- Security Incident Response: /docs/seguranca/incident-response-plan.md
- Disaster Recovery: /docs/operacao/disaster-recovery.md
- Database Runbook: /docs/operacao/database-runbook.md
```

---

## Apêndices

### A. Glossário de Termos

| Termo | Definição |
|-------|-----------|
| **P0/P1/P2** | Prioridades de incidente (P0=Crítico, P1=Alto, P2=Médio) |
| **RTO** | Recovery Time Objective - Tempo máximo de downtime aceitável |
| **RPO** | Recovery Point Objective - Perda de dados máxima aceitável |
| **Canary Deploy** | Deploy gradual, começando com pequeno % de tráfego |
| **Rollback** | Reverter para versão anterior |
| **Runbook** | Documento com procedimentos operacionais |
| **Postmortem** | Análise pós-incidente para aprender e melhorar |
| **SLA** | Service Level Agreement - Acordo de nível de serviço |
| **SLO** | Service Level Objective - Objetivo de nível de serviço |
| **On-Call** | Engenheiro de plantão responsável por responder alertas |
| **Guardrails** | Validações de segurança em inputs/outputs do agente |
| **Handoff** | Transferência de turno on-call |
| **Fallback** | Comportamento alternativo quando algo falha |

### B. Comandos Rápidos (Cheat Sheet)

```bash
# HEALTH CHECK
curl https://api.example.com/health

# VER PODS
kubectl get pods -l app=agente-api

# LOGS (últimos 100 linhas)
kubectl logs deployment/agente-api --tail=100

# LOGS (tempo real)
kubectl logs -f deployment/agente-api

# RESTART
kubectl rollout restart deployment/agente-api

# SCALE
kubectl scale deployment agente-api --replicas=20

# ROLLBACK
kubectl rollout undo deployment/agente-api

# MÉTRICAS
curl https://api.example.com/metrics | grep agent_requests_total

# DATABASE
kubectl exec -it postgres-pod -- psql -U user -d agente_ia

# REDIS
kubectl exec -it redis-pod -- redis-cli

# TOP RECURSOS
kubectl top pods -l app=agente-api

# VER VERSÃO ATUAL
curl https://api.example.com/version
```

### C. Status Codes e Significados

| Status Code | Significado | Ação |
|-------------|-------------|------|
| **200 OK** | Requisição bem sucedida | Nenhuma |
| **400 Bad Request** | Input inválido | Verificar validação de input |
| **401 Unauthorized** | Autenticação falhou | Verificar API key |
| **429 Too Many Requests** | Rate limit excedido | Implementar backoff, verificar se é ataque |
| **500 Internal Server Error** | Erro no servidor | Ver logs, identificar exceção |
| **502 Bad Gateway** | Problema no gateway/LB | Verificar API Gateway/Nginx |
| **503 Service Unavailable** | Serviço indisponível | Verificar pods, DB, Redis |
| **504 Gateway Timeout** | Timeout | Verificar latência, scale out |

---

## Histórico de Versões

| Versão | Data | Autor | Mudanças |
|--------|------|-------|----------|
| 1.0 | 2024-01-20 | Tech Team | Versão inicial completa |

---

## Feedback e Melhorias

Este runbook é um documento vivo. Se você:
- Encontrou informação faltando
- Usou um procedimento que não funcionou
- Tem sugestão de melhoria

**Por favor:**
1. Abra um PR com a correção/melhoria
2. Ou crie um issue no GitHub
3. Ou mencione no Slack #engineering

**Revisão:** Este runbook deve ser revisado mensalmente e atualizado sempre que houver mudanças significativas no sistema.

---

**Lembre-se:**
- Não entre em pânico
- Siga os procedimentos
- Comunique claramente
- Documente tudo
- Escale quando necessário
- Aprenda com cada incidente

**Você não está sozinho. O time está aqui para ajudar.**
