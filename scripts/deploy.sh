#!/usr/bin/env bash
# Usage: scripts/deploy.sh <image-tag> [extra helm args]
# KUBE_CONTEXT picks the cluster, the default is the current kubectl context.
set -euo pipefail
tag="${1:?usage: deploy.sh <image-tag>}"; shift
ctx="${KUBE_CONTEXT:-$(kubectl config current-context)}"
kubectl --context "$ctx" apply -f k8s/namespace.yaml
helm upgrade --install placetrack helm/placetrack --kube-context "$ctx" -n placetrack --reuse-values \
  --set image.tag="$tag" --wait --timeout 300s "$@"
kubectl --context "$ctx" -n placetrack get pods
