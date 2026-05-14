#!/bin/bash
set -euo pipefail

NAMESPACE="distributed-app"

echo "======================================"
echo " Déploiement K3s — distributed-app"
echo " Date : $(date '+%Y-%m-%d %H:%M:%S')"
echo "======================================"

# ── 1. Namespace ──────────────────────────────────────────────
echo ""
echo "[1/7] Namespace..."
kubectl apply -f namespace.yaml

# ── 2. Secrets & ConfigMaps ───────────────────────────────────
echo ""
echo "[2/7] Secrets & ConfigMaps..."
for svc in auth-service orders-service products-service payment-service interation-service; do
  kubectl apply -f ${svc}/secret.yaml
  kubectl apply -f ${svc}/configmap.yaml
done

# ── 3. Postgres ───────────────────────────────────────────────
echo ""
echo "[3/7] Postgres..."
kubectl apply -f postgres/
echo "Attente des pods Postgres..."
kubectl wait --for=condition=Ready pods -l app=postgres-auth -n ${NAMESPACE} --timeout=120s
kubectl wait --for=condition=Ready pods -l app=postgres-orders -n ${NAMESPACE} --timeout=120s
kubectl wait --for=condition=Ready pods -l app=postgres-products -n ${NAMESPACE} --timeout=120s
kubectl wait --for=condition=Ready pods -l app=postgres-payment -n ${NAMESPACE} --timeout=120s
kubectl wait --for=condition=Ready pods -l app=postgres-interation -n ${NAMESPACE} --timeout=120s
echo "Tous les Postgres sont prêts."

# ── 4. Services Django ────────────────────────────────────────
echo ""
echo "[4/7] Services Django..."
for svc in auth-service orders-service products-service payment-service interation-service; do
  kubectl apply -f ${svc}/deployment.yaml
  kubectl apply -f ${svc}/service.yaml
done

# ── 5. Frontend ───────────────────────────────────────────────
echo ""
echo "[5/7] Frontend..."
kubectl apply -f frontend/deployment.yaml
kubectl apply -f frontend/service.yaml

# ── 6. Ingress ────────────────────────────────────────────────
echo ""
echo "[6/7] Ingress..."
kubectl apply -f ingress-routes.yaml

# ── Résumé ────────────────────────────────────────────────────
echo ""
echo "======================================"
echo " Attente que tous les pods soient Ready..."
echo "======================================"
kubectl wait --for=condition=Ready pods --all -n ${NAMESPACE} --timeout=300s

echo ""
kubectl get pods -n ${NAMESPACE}

# ── 7. Port-forward Admin ────────────────────────────────────
echo ""
echo "[7/7] Port-forward pour les admin Django..."

# Fermer les port-forwards existants
pkill -f "kubectl port-forward" 2>/dev/null || true
sleep 2

kubectl port-forward svc/auth-service 9001:8000 -n ${NAMESPACE} &
kubectl port-forward svc/products-service 9002:8000 -n ${NAMESPACE} &
kubectl port-forward svc/orders-service 9003:8000 -n ${NAMESPACE} &
kubectl port-forward svc/payment-service 9004:8000 -n ${NAMESPACE} &
kubectl port-forward svc/interation-service 9005:8000 -n ${NAMESPACE} &

echo ""
echo "======================================"
echo " Déploiement terminé."
echo "======================================"
echo ""
echo " API    : curl http://distributed-app.local/api/auth/health/"
echo ""
echo " Admin  :"
echo "   Auth       → http://localhost:9001/admin/"
echo "   Products   → http://localhost:9002/admin/"
echo "   Orders     → http://localhost:9003/admin/"
echo "   Payments   → http://localhost:9004/admin/"
echo "   Interation → http://localhost:9005/admin/"