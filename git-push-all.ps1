#!/usr/bin/env pwsh
# Script para enviar commits para todos os remotes configurados
# Uso: .\git-push-all.ps1 [branch]

$branch = if ($args[0]) { $args[0] } else { "main" }
Write-Host "Enviando branch '$branch' para todos os remotes..."

$remotes = git remote
foreach ($remote in $remotes) {
      Write-Host "`nEnviando para $remote..."
      git push $remote $branch
      if ($LASTEXITCODE -ne 0) {
            Write-Host "Aviso: Não foi possível enviar para $remote. Continuando com os próximos..." -ForegroundColor Yellow
      }
      else {
            Write-Host "Enviado com sucesso para $remote." -ForegroundColor Green
      }
}

Write-Host "`nOperação concluída!" -ForegroundColor Cyan
