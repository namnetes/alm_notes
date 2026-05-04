#!/usr/bin/env bash
set -euo pipefail

IMAGE="zdev-vscode:latest"
PROXY="${HTTP_PROXY:-http://??????:3128}"

echo "Nettoyage du cache de build Docker..."
docker builder prune -a -f

echo "Build de l'image $IMAGE pour macOS Apple Silicon (ARM64)..."
docker build \
  --platform linux/arm64 \
  -f Dockerfile.macos \
  --build-arg HTTP_PROXY="$PROXY" \
  --build-arg HTTPS_PROXY="$PROXY" \
  --build-arg PROXY_HOST="$PROXY" \
  -t "$IMAGE" \
  .

echo "Build terminé : $IMAGE"
