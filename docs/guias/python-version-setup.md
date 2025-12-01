# Guia: Configuração de Versão Python Correta

## Problema Comum

Se você encontrou este erro ao instalar dependências:

```
ERROR: Ignored the following versions that require a different python version...
ERROR: Could not find a version that satisfies the requirement...
```

**Causa:** Você provavelmente está usando Python 3.13+, mas este projeto requer **Python 3.10-3.12**.

## Versões Python Suportadas

### ✅ Versões Recomendadas (Totalmente Suportadas)

- **Python 3.12.x** (RECOMENDADO - mais recente e estável)
- **Python 3.11.x** (Estável, bem testado)
- **Python 3.10.x** (Estável, amplamente usado)

### ⚠️ Versões NÃO Suportadas

- **Python 3.13+** - ChromaDB, CrewAI e outras libs ainda não suportam
- **Python 3.9 ou anterior** - Versões antigas, falta de features modernas

## Por Que Python 3.13 Não Funciona?

Bibliotecas essenciais do projeto ainda não suportam Python 3.13:

| Biblioteca | Versão Requerida | Status Python 3.13 |
|-----------|------------------|-------------------|
| ChromaDB | Requer Python <=3.12 | ❌ Não suportado |
| CrewAI | Requer Python <=3.12 | ❌ Não suportado |
| AGNO | Versões podem variar | ⚠️ Compatibilidade limitada |
| faiss-cpu | >= 1.9.0 | ✅ Suportado |

## Solução: Instalar Python 3.12

### Verificar Versão Atual

```bash
python --version
# ou
python3 --version
```

Se mostrar `Python 3.13.x`, você precisa instalar Python 3.12.

### Opção 1: pyenv (Recomendado - Gerenciador de Versões)

**pyenv** permite ter múltiplas versões do Python instaladas e trocar facilmente entre elas.

#### macOS/Linux

```bash
# 1. Instalar pyenv (se não tiver)
# macOS com Homebrew:
brew install pyenv

# Linux:
curl https://pyenv.run | bash

# 2. Adicionar ao shell (adicione ao ~/.zshrc ou ~/.bashrc)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init --path)"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

# 3. Reiniciar terminal ou:
source ~/.zshrc

# 4. Instalar Python 3.12
pyenv install 3.12.7

# 5. Definir como versão local para este projeto
cd /caminho/para/Python_Structure
pyenv local 3.12.7

# 6. Verificar
python --version
# Deve mostrar: Python 3.12.7
```

#### Windows

```powershell
# 1. Instalar pyenv-win com PowerShell
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"

# 2. Reiniciar PowerShell

# 3. Instalar Python 3.12
pyenv install 3.12.7

# 4. Definir como versão local
cd C:\caminho\para\Python_Structure
pyenv local 3.12.7

# 5. Verificar
python --version
```

### Opção 2: Instalação Direta (Sem pyenv)

#### macOS

```bash
# 1. Com Homebrew
brew install python@3.12

# 2. Criar link
brew link python@3.12

# 3. Usar python3.12 explicitamente ao criar venv
python3.12 -m venv venv
```

#### Windows

1. Baixar instalador: https://www.python.org/downloads/release/python-3127/
2. Executar instalador
3. ✅ Marcar "Add Python to PATH"
4. Instalar

#### Linux (Ubuntu/Debian)

```bash
# 1. Adicionar PPA deadsnakes
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# 2. Instalar Python 3.12
sudo apt install python3.12 python3.12-venv python3.12-dev

# 3. Usar python3.12 explicitamente
python3.12 -m venv venv
```

### Opção 3: conda/miniconda (Para Cientistas de Dados)

```bash
# 1. Criar ambiente conda com Python 3.12
conda create -n ai-agents python=3.12

# 2. Ativar ambiente
conda activate ai-agents

# 3. Verificar
python --version

# 4. Instalar dependências
pip install -r requirements.txt
```

## Configurar Ambiente Virtual com Python 3.12

Após instalar Python 3.12, configure o ambiente virtual:

### Com pyenv (Recomendado)

```bash
# 1. Navegar para o projeto
cd /Users/mateusolinto/Developer\ Projects/Templates\ -\ Criação\ IA/Python_Structure

# 2. Definir versão local
pyenv local 3.12.7

# 3. Criar venv
python -m venv venv

# 4. Ativar
source venv/bin/activate  # macOS/Linux
# ou
.\venv\Scripts\activate  # Windows

# 5. Verificar que está usando Python 3.12
python --version
which python  # Deve apontar para venv/bin/python

# 6. Atualizar pip
pip install --upgrade pip

# 7. Instalar dependências
pip install -r requirements.txt
```

### Sem pyenv

```bash
# 1. Navegar para o projeto
cd /caminho/para/Python_Structure

# 2. Criar venv com Python 3.12 explicitamente
python3.12 -m venv venv  # Ajuste para python3.12 se necessário

# 3. Ativar
source venv/bin/activate  # macOS/Linux
# ou
.\venv\Scripts\activate  # Windows

# 4. Verificar
python --version

# 5. Atualizar pip
pip install --upgrade pip

# 6. Instalar dependências
pip install -r requirements.txt
```

## Verificar Instalação

Após configurar tudo, execute este script de verificação:

```bash
python -c "
import sys
print(f'Python version: {sys.version}')
assert sys.version_info >= (3, 10), 'Python 3.10+ required'
assert sys.version_info < (3, 13), 'Python 3.13+ not supported yet'
print('✅ Python version is compatible!')

# Testar imports principais
try:
    import agno
    print('✅ AGNO installed')
except ImportError:
    print('❌ AGNO not installed')

try:
    import crewai
    print('✅ CrewAI installed')
except ImportError:
    print('❌ CrewAI not installed')

try:
    import chromadb
    print('✅ ChromaDB installed')
except ImportError:
    print('❌ ChromaDB not installed')

try:
    import openai
    print('✅ OpenAI installed')
except ImportError:
    print('❌ OpenAI not installed')

print('\\n🎉 Environment is ready!')
"
```

## Troubleshooting

### Erro: "No module named 'agno'"

**Causa:** Ambiente virtual não ativado ou dependências não instaladas.

**Solução:**
```bash
# Ativar venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### Erro: "command not found: python"

**Causa:** Python não está no PATH.

**Solução:**
```bash
# Tente usar python3
python3 --version

# Ou adicione Python ao PATH (varia por OS)
```

### Erro: ChromaDB ainda não instala

**Causa:** Pode estar usando Python 3.13 mesmo dentro do venv.

**Solução:**
```bash
# Dentro do venv, verificar versão
python --version

# Se ainda 3.13, recrie venv com python3.12
deactivate
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Múltiplas Versões Python Confusas

**Causa:** Várias instalações de Python no sistema.

**Solução:**
```bash
# Usar pyenv para gerenciar (Opção 1 acima)
# Ou usar caminho completo:
/usr/local/bin/python3.12 -m venv venv
```

## Script de Setup Automatizado

Criamos um script que verifica tudo automaticamente:

```bash
# Tornar executável
chmod +x scripts/setup-environment.sh

# Executar
./scripts/setup-environment.sh
```

O script:
1. ✅ Verifica versão Python
2. ✅ Cria venv se necessário
3. ✅ Instala dependências
4. ✅ Verifica que tudo funciona
5. ✅ Configura .env

## Resumo: Quick Start

**Se você tem Python 3.13:**

```bash
# 1. Instalar pyenv
brew install pyenv  # macOS
# ou seguir instruções acima para Linux/Windows

# 2. Instalar Python 3.12
pyenv install 3.12.7

# 3. No diretório do projeto
cd Python_Structure
pyenv local 3.12.7

# 4. Criar e ativar venv
python -m venv venv
source venv/bin/activate

# 5. Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# 6. Copiar .env
cp .env.example .env

# 7. Editar .env com suas API keys
nano .env  # ou use seu editor favorito
```

**Se você tem Python 3.10-3.12:**

```bash
# 1. Criar venv
python -m venv venv

# 2. Ativar
source venv/bin/activate

# 3. Instalar
pip install -r requirements.txt

# 4. Configurar .env
cp .env.example .env
```

## Recursos Adicionais

- [pyenv GitHub](https://github.com/pyenv/pyenv)
- [Python Downloads](https://www.python.org/downloads/)
- [Virtual Environments - Docs](https://docs.python.org/3/tutorial/venv.html)
- [Setup Ambiente - Guia Completo](./setup-ambiente.md)

## Suporte

Se continuar tendo problemas:

1. Verifique versão: `python --version`
2. Verifique que venv está ativo: `which python`
3. Recrie venv do zero
4. Consulte [Troubleshooting](./troubleshooting.md)
5. Abra issue no GitHub com output do erro completo
