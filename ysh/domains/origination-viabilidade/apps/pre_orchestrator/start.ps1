# Script para iniciar o serviço PRE Orchestrator no Windows

# Diretório base
$BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$BaseDir\.."

# Ambiente
$Env = if ($args[0]) { $args[0] } else { "development" }
$ConfigFile = "config\$Env.env"

# Verifica se o arquivo de configuração existe
if (-not (Test-Path $ConfigFile)) {
    Write-Host "Arquivo de configuração $ConfigFile não encontrado!" -ForegroundColor Red
    exit 1
}

# Carrega variáveis de ambiente
Get-Content $ConfigFile | ForEach-Object {
    if (-not ($_.StartsWith('#')) -and ($_.Trim() -ne '')) {
        $key, $value = $_.Split('=', 2)
        Set-Item -Path "env:$key" -Value $value
    }
}

# Inicializa o banco de dados, se necessário
if ($env:INIT_DB -eq "true") {
    Write-Host "Inicializando banco de dados..." -ForegroundColor Yellow
    python -m migrations.01_initialize_pre_orchestrator
}

# Define a flag de reload
$ReloadFlag = if ($env:RELOAD -eq "true") { "--reload" } else { "" }

# Inicia o servidor
Write-Host "Iniciando o servidor PRE Orchestrator em modo $Env..." -ForegroundColor Green
$Host = if ($env:HOST) { $env:HOST } else { "0.0.0.0" }
$Port = if ($env:PORT) { $env:PORT } else { "8020" }

uvicorn pkg.pre_orchestrator.server:app --host $Host --port $Port $ReloadFlag