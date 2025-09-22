#!/bin/bash
# Script para inicializar o ambiente de desenvolvimento

set -e

echo "Configurando ambiente de desenvolvimento para o PRE Orchestrator..."

# Verifica dependências
if ! command -v python3 &> /dev/null; then
    echo "Python 3 não encontrado. Por favor, instale o Python 3.10 ou superior."
    exit 1
fi

if ! command -v pip &> /dev/null; then
    echo "Pip não encontrado. Por favor, instale o pip."
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "Docker não encontrado. É recomendado instalar o Docker para os serviços dependentes."
    read -p "Continuar sem Docker? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Diretório base
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$BASE_DIR/.."

# Cria ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativa ambiente virtual
source venv/bin/activate

# Instala dependências
echo "Instalando dependências..."
pip install -r apps/pre_orchestrator/requirements.txt
pip install -r requirements-dev.txt

# Verifica se o Docker está disponível para iniciar os serviços dependentes
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "Iniciando serviços dependentes com Docker..."
    cd apps/pre_orchestrator
    docker-compose up -d postgres nats
fi

echo "Ambiente configurado com sucesso!"
echo "Para iniciar o servidor PRE Orchestrator, execute:"
echo "  cd apps/pre_orchestrator && ./start.sh"
