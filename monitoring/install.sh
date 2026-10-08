#!/usr/bin/env bash
# Installs kube-prometheus-stack and the PlaceTrack dashboard.
# Grafana password: kubectl -n monitoring get secret grafana-admin -o jsonpath='{.data.admin-password}' | base64 -d
set -euo pipefail
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f - >/dev/null
if ! kubectl -n monitoring get secret grafana-admin >/dev/null 2>&1; then
  kubectl -n monitoring create secret generic grafana-admin \
    --from-literal=admin-user=admin --from-literal=admin-password="$(openssl rand -hex 16)"
fi
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null
helm repo update >/dev/null
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring -f monitoring/values.yaml --wait --timeout 600s
kubectl -n monitoring create configmap placetrack-dashboard \
  --from-file=placetrack.json=monitoring/grafana-dashboard.json --dry-run=client -o yaml | kubectl apply -f -
kubectl -n monitoring label configmap placetrack-dashboard grafana_dashboard=1 --overwrite
