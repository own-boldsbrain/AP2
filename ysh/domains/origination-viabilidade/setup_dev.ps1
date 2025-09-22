# Script para inicializar o ambiente de desenvolvimento no Windows

# Verifica dependências
$errorCount = 0

function Test-CommandExists {
    param (
        [string]$command,
        [string]$message
    )
    
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
        Write-Host $message -ForegroundColor Red
        return $false
    }
    return $true
}

if (-not (Check-Command "python" "Python não encontrado. Por favor, instale o Python 3.10 ou superior.")) {
    $errorCount++
}

if (-not (Check-Command "pip" "Pip não encontrado. Por favor, instale o pip.")) {
    $errorCount++
}

if (-not (Check-Command "docker" "Docker não encontrado. É recomendado instalar o Docker para os serviços dependentes.")) {
    $answer = Read-Host "Continuar sem Docker? (y/n)"
    if ($answer -ne "y") {
        exit 1
    }
}

if ($errorCount -gt 0) {
    exit 1
}

# Diretório base
$BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $BaseDir

# Cria ambiente virtual se não existir
if (-not (Test-Path "venv")) {
    Write-Host "Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv venv
}

# Ativa ambiente virtual
Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
. .\venv\Scripts\Activate.ps1

# Instala dependências
Write-Host "Instalando dependências..." -ForegroundColor Yellow
pip install -r apps\pre_orchestrator\requirements.txt
pip install -r requirements-dev.txt

# Verifica se o Docker está disponível para iniciar os serviços dependentes
if ((Get-Command "docker" -ErrorAction SilentlyContinue) -and (Get-Command "docker-compose" -ErrorAction SilentlyContinue)) {
    Write-Host "Iniciando serviços dependentes com Docker..." -ForegroundColor Yellow
    Set-Location apps\pre_orchestrator
    docker-compose up -d postgres nats
    Set-Location ..\..
}

Write-Host "Ambiente configurado com sucesso!" -ForegroundColor Green
Write-Host "Para iniciar o servidor PRE Orchestrator, execute:" -ForegroundColor Cyan
Write-Host "  cd apps\pre_orchestrator && .\start.ps1" -ForegroundColor Cyan