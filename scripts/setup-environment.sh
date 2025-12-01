#!/bin/bash
# ==============================================================================
# Script de Setup do Ambiente - Python AI Agents Template
# ==============================================================================
# Este script automatiza a configuração do ambiente de desenvolvimento
#
# Uso: ./scripts/setup-environment.sh
# ==============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# ==============================================================================
# 1. Check Python Version
# ==============================================================================
print_header "1. Verificando Versão do Python"

PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "Versão detectada: Python $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -eq 3 ]; then
    if [ "$PYTHON_MINOR" -ge 10 ] && [ "$PYTHON_MINOR" -le 12 ]; then
        print_success "Python $PYTHON_VERSION é compatível (3.10-3.12)"
    elif [ "$PYTHON_MINOR" -ge 13 ]; then
        print_error "Python $PYTHON_VERSION NÃO é suportado!"
        print_warning "Este projeto requer Python 3.10, 3.11 ou 3.12"
        print_info "Python 3.13+ ainda não é suportado por ChromaDB e CrewAI"
        echo ""
        echo "Soluções:"
        echo "  1. Instalar pyenv: brew install pyenv (macOS) ou apt install pyenv (Linux)"
        echo "  2. Instalar Python 3.12: pyenv install 3.12.7"
        echo "  3. Definir versão local: pyenv local 3.12.7"
        echo "  4. Executar este script novamente"
        echo ""
        echo "Guia completo: docs/guias/python-version-setup.md"
        exit 1
    else
        print_error "Python $PYTHON_VERSION é muito antigo!"
        print_warning "Requer Python 3.10 ou superior"
        exit 1
    fi
else
    print_error "Python 3 não encontrado!"
    exit 1
fi

# ==============================================================================
# 2. Check if venv exists
# ==============================================================================
print_header "2. Verificando Ambiente Virtual"

if [ -d "venv" ]; then
    print_info "Ambiente virtual já existe em ./venv"
    read -p "Deseja recriar o ambiente virtual? (s/N): " RECREATE
    if [ "$RECREATE" = "s" ] || [ "$RECREATE" = "S" ]; then
        print_info "Removendo ambiente virtual existente..."
        rm -rf venv
        print_success "Ambiente virtual removido"
    else
        print_info "Usando ambiente virtual existente"
    fi
fi

if [ ! -d "venv" ]; then
    print_info "Criando ambiente virtual..."
    python -m venv venv
    print_success "Ambiente virtual criado em ./venv"
fi

# ==============================================================================
# 3. Activate venv
# ==============================================================================
print_header "3. Ativando Ambiente Virtual"

# Detect OS
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # macOS/Linux
    source venv/bin/activate
fi

print_success "Ambiente virtual ativado"
print_info "Python no venv: $(which python)"
print_info "Versão no venv: $(python --version)"

# ==============================================================================
# 4. Upgrade pip
# ==============================================================================
print_header "4. Atualizando pip"

python -m pip install --upgrade pip
print_success "pip atualizado para versão $(pip --version | awk '{print $2}')"

# ==============================================================================
# 5. Install dependencies
# ==============================================================================
print_header "5. Instalando Dependências"

print_info "Isto pode levar alguns minutos..."
echo ""

if pip install -r requirements.txt; then
    print_success "Todas as dependências instaladas com sucesso!"
else
    print_error "Falha ao instalar dependências"
    print_warning "Verifique os erros acima"
    echo ""
    echo "Problemas comuns:"
    echo "  - Versão Python incorreta (use 3.10-3.12)"
    echo "  - Falta de ferramentas de build (gcc, etc)"
    echo "  - Problemas de rede"
    echo ""
    echo "Consulte: docs/guias/troubleshooting.md"
    exit 1
fi

# ==============================================================================
# 6. Verify installations
# ==============================================================================
print_header "6. Verificando Instalações"

echo "Testando imports principais..."
echo ""

python -c "
import sys

# Test core frameworks
packages = {
    'agno': 'AGNO (Single-Agent Framework)',
    'crewai': 'CrewAI (Multi-Agent Framework)',
    'openai': 'OpenAI',
    'chromadb': 'ChromaDB (Vector Store)',
    'fastapi': 'FastAPI',
    'pydantic': 'Pydantic',
}

failed = []
for package, name in packages.items():
    try:
        __import__(package)
        print(f'✅ {name}')
    except ImportError:
        print(f'❌ {name}')
        failed.append(package)

if failed:
    print(f'\n❌ Falha ao importar: {", ".join(failed)}')
    sys.exit(1)
else:
    print('\n✅ Todas as bibliotecas principais importadas com sucesso!')
"

if [ $? -eq 0 ]; then
    print_success "Verificação de imports concluída"
else
    print_error "Alguns imports falharam"
    exit 1
fi

# ==============================================================================
# 7. Setup .env file
# ==============================================================================
print_header "7. Configurando Arquivo .env"

if [ -f ".env" ]; then
    print_info "Arquivo .env já existe"
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Arquivo .env criado a partir de .env.example"
        print_warning "IMPORTANTE: Edite o arquivo .env e adicione suas API keys!"
        echo ""
        echo "API Keys necessárias:"
        echo "  - OPENAI_API_KEY (para GPT-4, GPT-3.5, etc)"
        echo "  - ANTHROPIC_API_KEY (opcional - para Claude)"
        echo "  - GOOGLE_API_KEY (opcional - para Gemini)"
        echo ""
    else
        print_warning "Arquivo .env.example não encontrado"
    fi
fi

# ==============================================================================
# 8. Create data directories
# ==============================================================================
print_header "8. Criando Diretórios de Dados"

mkdir -p data/memory
mkdir -p data/knowledge_base
mkdir -p data/logs
mkdir -p data/exports

print_success "Diretórios criados:"
echo "  - data/memory (SQLite databases)"
echo "  - data/knowledge_base (ChromaDB collections)"
echo "  - data/logs (Application logs)"
echo "  - data/exports (Exported data)"

# ==============================================================================
# 9. Final Summary
# ==============================================================================
print_header "✨ Setup Completo!"

echo -e "${GREEN}Ambiente configurado com sucesso!${NC}"
echo ""
echo "Próximos passos:"
echo ""
echo "1. Editar arquivo .env com suas API keys:"
echo "   ${YELLOW}nano .env${NC}"
echo ""
echo "2. Ativar ambiente virtual (em novos terminais):"
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "   ${YELLOW}.\\venv\\Scripts\\activate${NC}"
else
    echo "   ${YELLOW}source venv/bin/activate${NC}"
fi
echo ""
echo "3. Explorar exemplos:"
echo "   ${YELLOW}cd examples/simple-chatbot && python main.py${NC}"
echo ""
echo "4. Ler documentação:"
echo "   ${YELLOW}docs/guias/quick-start.md${NC}"
echo ""
echo "5. Criar seu primeiro agente:"
echo "   ${YELLOW}docs/guias/criar-agente.md${NC}"
echo ""
print_success "Ambiente pronto para desenvolvimento! 🚀"
echo ""
