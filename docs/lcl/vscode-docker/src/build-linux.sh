#!/usr/bin/env bash
set -euo pipefail

IMAGE="zdev-vscode:latest"

echo "Nettoyage du cache de build Docker..."
docker builder prune -a -f

echo "Build de l'image $IMAGE pour Linux AMD64..."
docker build \
  -f Dockerfile.linux \
  -t "$IMAGE" \
  .

echo "Build terminé : $IMAGE"
