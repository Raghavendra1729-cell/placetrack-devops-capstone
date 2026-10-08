#!/usr/bin/env bash
# Usage: scripts/deploy.sh <image-tag> [extra helm args]
set -euo pipefail
tag="${1:?usage: deploy.sh <image-tag>}"; shift
kubectl apply -f k8s/namespace.yaml
helm upgrade --install placetrack helm/placetrack -n placetrack \
  --set image.tag="$tag" --wait --timeout 300s "$@"
kubectl -n placetrack get pods
