#!/usr/bin/env bash
# Usage: scripts/deploy.sh <image-tag> [extra helm args...]
# Deploys the chart with the given image tag (a commit SHA when images come from the registry).
set -euo pipefail
tag="${1:?usage: deploy.sh <image-tag>}"; shift
kubectl apply -f k8s/namespace.yaml
helm upgrade --install placetrack helm/placetrack -n placetrack \
  --set image.tag="$tag" --wait --timeout 300s "$@"
kubectl -n placetrack get pods
