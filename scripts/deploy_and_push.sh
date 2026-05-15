#!/usr/bin/env bash
set -euo pipefail

# Script de deploy: constrói imagens backend/dashboard e publica no Docker Hub.
# Uso: execute na raiz do repositório: ./scripts/deploy_and_push.sh
# Opcional: definir DOCKER_USER e DOCKER_PASSWORD para login não interativo.

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

echo "Atualizando código..."
git pull origin main

SHA=$(git rev-parse --short HEAD || echo "local")

# Login Docker Hub
if [ -n "${DOCKER_USER:-}" ] && [ -n "${DOCKER_PASSWORD:-}" ]; then
  echo "Fazendo login no Docker Hub como $DOCKER_USER (não interativo)"
  echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USER" --password-stdin
else
  echo "Por favor faça login no Docker Hub (interativo). Se preferir, exporte DOCKER_USER/DOCKER_PASSWORD para login automático."
  docker login
fi

echo "Construindo backend..."
docker build -t lucasplcorrea/chatwoot-history-backend:latest ./backend
docker tag lucasplcorrea/chatwoot-history-backend:latest lucasplcorrea/chatwoot-history-backend:$SHA

echo "Enviando backend para Docker Hub..."
docker push lucasplcorrea/chatwoot-history-backend:latest
docker push lucasplcorrea/chatwoot-history-backend:$SHA

echo "Construindo dashboard..."
docker build -t lucasplcorrea/chatwoot-history-dashboard:latest ./dashboard
docker tag lucasplcorrea/chatwoot-history-dashboard:latest lucasplcorrea/chatwoot-history-dashboard:$SHA

echo "Enviando dashboard para Docker Hub..."
docker push lucasplcorrea/chatwoot-history-dashboard:latest
docker push lucasplcorrea/chatwoot-history-dashboard:$SHA

echo "Atualizando containers locais..."
docker-compose pull || true
docker-compose up -d --no-deps --build backend dashboard

echo "Status dos containers:"
docker-compose ps -a

echo "Deploy concluído. Imagens publicadas com tag latest e $SHA."
