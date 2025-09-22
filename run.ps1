# AP2 Agents Orchestration Script
# Este script inicia todos os agentes necessários para demonstração do AP2
# Certifique-se de que o ambiente Python esteja configurado corretamente com uv

# Configurações
$PythonPath = "uv" # Altere para o caminho do seu ambiente Python se necessário
$BaseDir = "C:\Users\fjuni\Documents\AP2"
$SampleDir = Join-Path $BaseDir "samples\python"
$LogDir = Join-Path $BaseDir "logs"

# Criar diretório de logs se não existir
if (-not (Test-Path $LogDir)) {
    New-Item -Path $LogDir -ItemType Directory | Out-Null
    Write-Host "Diretório de logs criado em $LogDir"
}

# Função para iniciar um agente em uma nova janela PowerShell
function Start-Agent {
    param (
        [string]$AgentName,
        [string]$ModulePath,
        [int]$Port,
        [string]$AgentType
    )

    $LogFile = Join-Path $LogDir "$AgentName.log"
    $WorkingDir = Join-Path $SampleDir "src\roles\$ModulePath"

    $command = "cd $WorkingDir; `$env:PORT=$Port; $PythonPath python -m $AgentType 2>&1 | Tee-Object -FilePath '$LogFile'"

    Write-Host "Iniciando $AgentName na porta $Port..." -ForegroundColor Green
    Start-Process pwsh -ArgumentList "-NoExit", "-Command", $command -WindowStyle Normal

    # Pequena pausa para garantir que o processo seja iniciado antes de continuar
    Start-Sleep -Seconds 2
}

# Limpar logs antigos
Remove-Item -Path (Join-Path $LogDir "*.log") -Force -ErrorAction SilentlyContinue
Write-Host "Logs antigos removidos" -ForegroundColor Yellow

# Verificar se uv está instalado
try {
    $uvVersion = & $PythonPath --version
    Write-Host "Usando Python: $uvVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Erro ao executar $PythonPath. Verifique se o comando está correto e instalado." -ForegroundColor Red
    exit 1
}

# Configurar variáveis de ambiente
$env:PYTHONPATH = $SampleDir

# Iniciar Shopping Agent
Start-Agent -AgentName "ShoppingAgent" -ModulePath "shopping_agent" -Port 8000 -AgentType "shopping_agent"

# Iniciar Merchant Agent
Start-Agent -AgentName "MerchantAgent" -ModulePath "merchant_agent" -Port 8001 -AgentType "merchant_agent"

# Iniciar Credentials Provider Agent
Start-Agent -AgentName "CredentialsProviderAgent" -ModulePath "credentials_provider_agent" -Port 8002 -AgentType "credentials_provider_agent"

# Iniciar Merchant Payment Processor Agent
Start-Agent -AgentName "MerchantPaymentProcessorAgent" -ModulePath "merchant_payment_processor_agent" -Port 8003 -AgentType "merchant_payment_processor_agent"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Todos os agentes AP2 foram iniciados!" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host "Shopping Agent: http://localhost:8000" -ForegroundColor White
Write-Host "Merchant Agent: http://localhost:8001" -ForegroundColor White
Write-Host "Credentials Provider: http://localhost:8002" -ForegroundColor White
Write-Host "Merchant Payment Processor: http://localhost:8003" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Os logs estão sendo salvos em: $LogDir" -ForegroundColor Yellow
Write-Host ""
Write-Host "Para testar os endpoints, você pode usar:" -ForegroundColor Magenta
Write-Host "curl http://localhost:8001/a2a/merchant_agent/.well-known/agent-card.json" -ForegroundColor White
Write-Host ""
Write-Host "Para encerrar todos os agentes, feche as janelas do PowerShell" -ForegroundColor Red
