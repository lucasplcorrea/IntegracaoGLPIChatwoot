# Script PowerShell para build e push de imagens Docker no Windows
# Uso: cd c:\...\IntegracaoGLPIChatwoot; .\scripts\deploy_and_push.ps1
# Após executar, na VPS: git pull origin main && docker-compose pull && docker-compose restart

param(
    [switch]$SkipPull = $false
)

$ErrorActionPreference = "Stop"

$REPO_DIR = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $REPO_DIR

Write-Host "=== Build e Push de Imagens Docker ===" -ForegroundColor Green

if (-not $SkipPull) {
    Write-Host "Atualizando código do GitHub..." -ForegroundColor Yellow
    git pull origin main
}

$SHA = (git rev-parse --short HEAD || "local").Trim()
Write-Host "Commit SHA: $SHA" -ForegroundColor Cyan

# Login Docker Hub
Write-Host "Verificando login no Docker Hub..." -ForegroundColor Yellow
docker login

# Build backend
Write-Host "Construindo backend..." -ForegroundColor Yellow
docker build -t lucasplcorrea/chatwoot-history-backend:latest ./backend
if ($LASTEXITCODE -ne 0) { throw "Erro ao fazer build da imagem backend" }

docker tag lucasplcorrea/chatwoot-history-backend:latest lucasplcorrea/chatwoot-history-backend:$SHA
Write-Host "Backend construído com sucesso" -ForegroundColor Green

# Push backend
Write-Host "Enviando backend para Docker Hub..." -ForegroundColor Yellow
docker push lucasplcorrea/chatwoot-history-backend:latest
docker push lucasplcorrea/chatwoot-history-backend:$SHA
Write-Host "Backend enviado com sucesso" -ForegroundColor Green

# Build dashboard
Write-Host "Construindo dashboard..." -ForegroundColor Yellow
docker build -t lucasplcorrea/chatwoot-history-dashboard:latest ./dashboard
if ($LASTEXITCODE -ne 0) { throw "Erro ao fazer build da imagem dashboard" }

docker tag lucasplcorrea/chatwoot-history-dashboard:latest lucasplcorrea/chatwoot-history-dashboard:$SHA
Write-Host "Dashboard construído com sucesso" -ForegroundColor Green

# Push dashboard
Write-Host "Enviando dashboard para Docker Hub..." -ForegroundColor Yellow
docker push lucasplcorrea/chatwoot-history-dashboard:latest
docker push lucasplcorrea/chatwoot-history-dashboard:$SHA
Write-Host "Dashboard enviado com sucesso" -ForegroundColor Green

Write-Host ""
Write-Host "=== Deploy Concluído ===" -ForegroundColor Green
Write-Host "Imagens publicadas com tags:" -ForegroundColor Cyan
Write-Host "  - lucasplcorrea/chatwoot-history-backend:latest"
Write-Host "  - lucasplcorrea/chatwoot-history-backend:$SHA"
Write-Host "  - lucasplcorrea/chatwoot-history-dashboard:latest"
Write-Host "  - lucasplcorrea/chatwoot-history-dashboard:$SHA"
Write-Host ""
Write-Host "Na VPS (/app/docker/chatwoot-history), execute:" -ForegroundColor Cyan
Write-Host "  git pull origin main" -ForegroundColor White
Write-Host "  docker-compose pull" -ForegroundColor White
Write-Host "  docker-compose restart" -ForegroundColor White
