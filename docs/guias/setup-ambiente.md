# Guia: Setup de Ambiente de Desenvolvimento

## Visão Geral

Este guia fornece instruções detalhadas para configurar um ambiente de desenvolvimento completo para projetos de Agentes de IA, incluindo Python, Node.js, dependências, ferramentas e configurações essenciais.

## Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Instalação Python](#instalação-python)
3. [Ambiente Virtual](#ambiente-virtual)
4. [Dependências](#dependências)
5. [Configuração de Secrets](#configuração-de-secrets)
6. [Ferramentas de Desenvolvimento](#ferramentas-de-desenvolvimento)
7. [IDE e Extensões](#ide-e-extensões)
8. [Docker](#docker)
9. [Databases](#databases)
10. [Verificação do Setup](#verificação-do-setup)

## Pré-requisitos

### Sistema Operacional

**macOS**:
```bash
# Instalar Homebrew (se não tiver)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar ferramentas base
brew install git curl wget
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt update
sudo apt install -y git curl wget build-essential
```

**Windows**:
```powershell
# Instalar Chocolatey (como administrador)
Set-ExecutionPolicy Bypass -Scope Process -Force; `
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; `
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Instalar ferramentas base
choco install git curl wget -y
```

### Git

```bash
# Configurar Git
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@empresa.com"

# Verificar
git config --list
```

## Instalação Python

### Python 3.9+

**macOS**:
```bash
# Instalar Python via Homebrew
brew install python@3.11

# Verificar versão
python3 --version  # Deve ser >= 3.9
```

**Linux**:
```bash
# Ubuntu/Debian
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Verificar
python3 --version
```

**Windows**:
```powershell
# Via Chocolatey
choco install python --version=3.11.0 -y

# Ou baixar de python.org
# https://www.python.org/downloads/
```

### Atualizar pip

```bash
python3 -m pip install --upgrade pip setuptools wheel
```

## Ambiente Virtual

### Criar Ambiente Virtual

```bash
# Navegar para o projeto
cd /caminho/para/seu-projeto

# Criar venv
python3 -m venv venv

# Alternativa: usar virtualenv
pip install virtualenv
virtualenv venv
```

### Ativar Ambiente

**macOS/Linux**:
```bash
source venv/bin/activate
```

**Windows**:
```powershell
.\venv\Scripts\activate
```

### Verificar Ativação

```bash
# Deve mostrar o caminho do Python dentro do venv
which python  # macOS/Linux
where python  # Windows

# Deve ter (venv) no prompt
# (venv) usuario@host:~/projeto$
```

### Desativar

```bash
deactivate
```

## Dependências

### Core Dependencies

```bash
# Com venv ativado
pip install --upgrade pip

# Instalar dependências principais
cat > requirements.txt << 'EOF'
# LLM Providers
openai==1.3.0
anthropic==0.7.0

# LangChain
langchain==0.1.0
langchain-community==0.0.10
langchain-openai==0.0.2

# Vector Databases
pinecone-client==3.0.0
chromadb==0.4.18

# API Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Utilities
python-dotenv==1.0.0
requests==2.31.0
tenacity==8.2.3  # Retry logic

# Logging & Monitoring
loguru==0.7.2
prometheus-client==0.19.0

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9  # PostgreSQL
pymongo==4.6.0  # MongoDB

# Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1
pytest-mock==3.12.0
httpx==0.25.2  # Para testar FastAPI

# Development
black==23.12.0  # Formatação
pylint==3.0.3  # Linting
mypy==1.7.1  # Type checking
ipython==8.18.1  # REPL melhorado
EOF

# Instalar
pip install -r requirements.txt
```

### Desenvolvimento

```bash
# Criar requirements-dev.txt
cat > requirements-dev.txt << 'EOF'
-r requirements.txt

# Debug
ipdb==0.13.13
pdb++==0.10.3

# Documentation
sphinx==7.2.6
sphinx-rtd-theme==2.0.0

# Pre-commit hooks
pre-commit==3.6.0

# Load testing
locust==2.20.0
EOF

# Instalar
pip install -r requirements-dev.txt
```

### Freeze Dependencies

```bash
# Criar arquivo com versões exatas
pip freeze > requirements-lock.txt

# Instalar a partir do lock
pip install -r requirements-lock.txt
```

## Configuração de Secrets

### Arquivo .env

```bash
# Criar .env
cat > .env << 'EOF'
# ========== LLM Providers ==========
OPENAI_API_KEY=sk-...
OPENAI_ORG_ID=org-...
ANTHROPIC_API_KEY=sk-ant-...

# ========== Vector Database ==========
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=agent-memory

# ========== APIs Externas ==========
CRM_API_KEY=...
CRM_API_URL=https://api.crm.com/v1

ERP_API_KEY=...
ERP_API_URL=https://api.erp.com

# ========== Database ==========
DATABASE_URL=postgresql://user:pass@localhost:5432/agentdb
MONGODB_URI=mongodb://localhost:27017/agentdb

# ========== Redis ==========
REDIS_URL=redis://localhost:6379/0

# ========== Application ==========
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=True

# ========== Security ==========
SECRET_KEY=your-secret-key-min-32-chars
JWT_SECRET=your-jwt-secret

# ========== Rate Limiting ==========
RATE_LIMIT_PER_MINUTE=60
MAX_RETRIES=3

# ========== Monitoring ==========
SENTRY_DSN=https://...@sentry.io/...
PROMETHEUS_PORT=9090
EOF

# Adicionar ao .gitignore
echo ".env" >> .gitignore
echo ".env.*" >> .gitignore
echo "!.env.example" >> .gitignore
```

### Criar .env.example

```bash
# Template sem secrets
cp .env .env.example

# Remover valores sensíveis (deixar apenas estrutura)
sed -i 's/=.*/=/' .env.example
```

### Carregar Secrets

```python
# config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurações da aplicação."""

    # LLM
    openai_api_key: str
    anthropic_api_key: Optional[str] = None

    # Vector DB
    pinecone_api_key: str
    pinecone_environment: str
    pinecone_index_name: str

    # Database
    database_url: str
    mongodb_uri: Optional[str] = None
    redis_url: str

    # Application
    environment: str = "development"
    log_level: str = "INFO"
    debug: bool = False

    # Security
    secret_key: str
    jwt_secret: str

    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton
settings = Settings()
```

## Ferramentas de Desenvolvimento

### Pre-commit Hooks

```bash
# Instalar pre-commit
pip install pre-commit

# Criar .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/PyCQA/pylint
    rev: v3.0.3
    hooks:
      - id: pylint
        args: [--disable=all, --enable=unused-import]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
EOF

# Instalar hooks
pre-commit install

# Rodar manualmente
pre-commit run --all-files
```

### Black (Formatação)

```bash
# Configurar Black
cat > pyproject.toml << 'EOF'
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.venv
  | venv
  | build
  | dist
)/
'''
EOF

# Formatar código
black src/ tests/

# Verificar sem modificar
black --check src/ tests/
```

### Pylint

```bash
# Criar .pylintrc
cat > .pylintrc << 'EOF'
[MASTER]
ignore=venv,.venv,tests
ignore-patterns=test_.*?\.py

[MESSAGES CONTROL]
disable=C0111,  # missing-docstring
        C0103,  # invalid-name
        R0903,  # too-few-public-methods

[FORMAT]
max-line-length=100

[DESIGN]
max-args=7
max-locals=20
EOF

# Rodar pylint
pylint src/
```

### Mypy (Type Checking)

```bash
# Configurar mypy
cat >> pyproject.toml << 'EOF'

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "tests.*"
ignore_errors = true
EOF

# Rodar mypy
mypy src/
```

## IDE e Extensões

### VS Code

**Extensões recomendadas**:

```json
// .vscode/extensions.json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "ms-toolsai.jupyter",
    "tamasfe.even-better-toml",
    "redhat.vscode-yaml",
    "eamodio.gitlens",
    "streetsidesoftware.code-spell-checker"
  ]
}
```

**Configurações**:

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.pylintPath": "${workspaceFolder}/venv/bin/pylint",
  "python.formatting.provider": "black",
  "python.formatting.blackPath": "${workspaceFolder}/venv/bin/black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestPath": "${workspaceFolder}/venv/bin/pytest",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true
  }
}
```

### PyCharm

1. Abrir projeto
2. Settings → Project → Python Interpreter
3. Adicionar → Existing Environment → `./venv/bin/python`
4. Tools → Python Integrated Tools → Testing: pytest
5. Settings → Tools → Black → Enable

## Docker

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Expor porta
EXPOSE 8000

# Comando
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/agentdb
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - .env
    depends_on:
      - db
      - redis
    volumes:
      - ./src:/app/src
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=agentdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  mongodb:
    image: mongo:7
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=password
    volumes:
      - mongodb_data:/data/db

volumes:
  postgres_data:
  redis_data:
  mongodb_data:
```

### Comandos Docker

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Logs
docker-compose logs -f app

# Stop
docker-compose down

# Rebuild e start
docker-compose up -d --build

# Executar comando no container
docker-compose exec app python -m pytest
```

## Databases

### PostgreSQL

**Instalação Local**:

```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Linux
sudo apt install postgresql-15
sudo systemctl start postgresql

# Windows
choco install postgresql -y
```

**Criar Database**:

```bash
# Criar database
createdb agentdb

# Conectar
psql agentdb

# Ou usar conexão completa
psql postgresql://localhost:5432/agentdb
```

**Migrations (Alembic)**:

```bash
# Instalar Alembic
pip install alembic

# Inicializar
alembic init migrations

# Criar migration
alembic revision --autogenerate -m "Initial migration"

# Aplicar
alembic upgrade head
```

### MongoDB

**Instalação**:

```bash
# macOS
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community

# Linux
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod

# Windows
choco install mongodb -y
```

**Uso**:

```bash
# Conectar
mongosh

# Via Python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["agentdb"]
```

### Redis

**Instalação**:

```bash
# macOS
brew install redis
brew services start redis

# Linux
sudo apt install redis-server
sudo systemctl start redis-server

# Windows
choco install redis -y
```

**Teste**:

```bash
# CLI
redis-cli ping
# PONG

# Python
import redis
r = redis.from_url("redis://localhost:6379/0")
r.ping()
```

## Verificação do Setup

### Script de Verificação

```python
# verify_setup.py
"""
Script para verificar se o ambiente está configurado corretamente.
"""

import sys
import importlib
from typing import List, Tuple


def check_python_version() -> Tuple[bool, str]:
    """Verifica versão do Python."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        return True, f"Python {version.major}.{version.minor}.{version.micro} ✓"
    return False, f"Python {version.major}.{version.minor}.{version.micro} ✗ (requer 3.9+)"


def check_package(package_name: str) -> Tuple[bool, str]:
    """Verifica se pacote está instalado."""
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, '__version__', 'unknown')
        return True, f"{package_name} {version} ✓"
    except ImportError:
        return False, f"{package_name} ✗ (não instalado)"


def check_env_file() -> Tuple[bool, str]:
    """Verifica se .env existe."""
    import os
    if os.path.exists('.env'):
        return True, ".env file ✓"
    return False, ".env file ✗ (não encontrado)"


def check_env_vars() -> List[Tuple[bool, str]]:
    """Verifica variáveis de ambiente essenciais."""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    required_vars = [
        "OPENAI_API_KEY",
        "DATABASE_URL",
        "SECRET_KEY"
    ]

    results = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            results.append((True, f"{var} ✓"))
        else:
            results.append((False, f"{var} ✗ (não configurado)"))

    return results


def check_database_connection() -> Tuple[bool, str]:
    """Verifica conexão com database."""
    try:
        from sqlalchemy import create_engine
        import os
        from dotenv import load_dotenv

        load_dotenv()

        engine = create_engine(os.getenv("DATABASE_URL"))
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True, "Database connection ✓"
    except Exception as e:
        return False, f"Database connection ✗ ({str(e)})"


def main():
    """Executa todas as verificações."""
    print("=" * 60)
    print("VERIFICAÇÃO DO AMBIENTE")
    print("=" * 60)

    all_checks = []

    # Python version
    result, message = check_python_version()
    all_checks.append(result)
    print(f"\n{message}")

    # Packages
    print("\nPACOTES:")
    packages = [
        "openai",
        "anthropic",
        "langchain",
        "fastapi",
        "sqlalchemy",
        "pytest",
        "black",
        "pylint"
    ]

    for package in packages:
        result, message = check_package(package)
        all_checks.append(result)
        print(f"  {message}")

    # .env file
    print("\nCONFIGURAÇÃO:")
    result, message = check_env_file()
    all_checks.append(result)
    print(f"  {message}")

    # Environment variables
    for result, message in check_env_vars():
        all_checks.append(result)
        print(f"  {message}")

    # Database
    print("\nDATABASE:")
    result, message = check_database_connection()
    all_checks.append(result)
    print(f"  {message}")

    # Summary
    print("\n" + "=" * 60)
    passed = sum(all_checks)
    total = len(all_checks)
    print(f"RESULTADO: {passed}/{total} verificações passaram")

    if passed == total:
        print("✓ Ambiente configurado corretamente!")
        return 0
    else:
        print("✗ Algumas verificações falharam. Veja acima.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

**Executar**:

```bash
python verify_setup.py
```

### Testes Rápidos

```bash
# Python e pip
python --version
pip --version

# Importar pacotes principais
python -c "import openai; import langchain; import fastapi; print('OK')"

# Conectar database
python -c "from sqlalchemy import create_engine; import os; from dotenv import load_dotenv; load_dotenv(); engine = create_engine(os.getenv('DATABASE_URL')); print('DB OK')"

# Redis
python -c "import redis; r = redis.from_url('redis://localhost:6379/0'); r.ping(); print('Redis OK')"
```

## Troubleshooting

### Erro: "command not found: python"

```bash
# Usar python3
python3 --version

# Ou criar alias
echo "alias python=python3" >> ~/.bashrc  # Linux
echo "alias python=python3" >> ~/.zshrc   # macOS
source ~/.bashrc  # ou ~/.zshrc
```

### Erro: "pip: No module named pip"

```bash
# Reinstalar pip
python -m ensurepip --upgrade
```

### Erro: "Permission denied" ao instalar pacotes

```bash
# Não usar sudo! Usar venv
python -m venv venv
source venv/bin/activate
pip install pacote
```

### Erro: "SSL Certificate verify failed"

```bash
# macOS: Instalar certificados
cd "/Applications/Python 3.11/"
./Install\ Certificates.command
```

### Problema: Imports não funcionam

```bash
# Adicionar diretório ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"

# Ou criar __init__.py
touch src/__init__.py
```

## Próximos Passos

- [Quick Start](quick-start.md): Criar primeiro projeto
- [Criar Agente](criar-agente.md): Implementar agentes
- [Testes](testes-conversacao.md): Configurar testes

## Referências

- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
