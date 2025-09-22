#!/bin/bash
# Script para iniciar o serviço PRE Orchestrator

set -e

# Diretório base
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$BASE_DIR/.."

# Ambiente
ENV=${1:-development}
CONFIG_FILE="config/$ENV.env"

# Verifica se o arquivo de configuração existe
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Arquivo de configuração $CONFIG_FILE não encontrado!"
    exit 1
fi

# Carrega variáveis de ambiente
export $(grep -v '^#' $CONFIG_FILE | xargs)

# Inicializa o banco de dados, se necessário
if [ "$INIT_DB" = "true" ]; then
    echo "Inicializando banco de dados..."
    python -m migrations.01_initialize_pre_orchestrator
fi

# Inicia o servidor
echo "Iniciando o servidor PRE Orchestrator em modo $ENV..."
uvicorn pkg.pre_orchestrator.server:app --host ${HOST:-0.0.0.0} --port ${PORT:-8020} ${RELOAD_FLAG:---reload}
