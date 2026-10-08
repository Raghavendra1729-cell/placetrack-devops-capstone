#!/usr/bin/env bash
set -euo pipefail
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null
helm repo update >/dev/null
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace -f monitoring/values.yaml --wait --timeout 600s
kubectl -n monitoring create configmap placetrack-dashboard \
  --from-file=placetrack.json=monitoring/grafana-dashboard.json --dry-run=client -o yaml | kubectl apply -f -
kubectl -n monitoring label configmap placetrack-dashboard grafana_dashboard=1 --overwrite
