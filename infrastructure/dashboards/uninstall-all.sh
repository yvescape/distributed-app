#!/usr/bin/env bash
# uninstall-all.sh — Désinstallation propre des dashboards d'observation
# Usage : sudo bash uninstall-all.sh [--full]
#   Sans flag  : supprime uniquement les Ingress (conserve les stacks)
#   --full     : supprime aussi ArgoCD et kube-prometheus-stack

set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✅ $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }

KUBE="k3s kubectl"
FULL_UNINSTALL=false
[[ "${1:-}" == "--full" ]] && FULL_UNINSTALL=true

echo "════════════════════════════════════════════════════════"
if $FULL_UNINSTALL; then
  echo "  Désinstallation COMPLÈTE (Ingress + stacks)"
else
  echo "  Désinstallation des Ingress uniquement"
  echo "  (utilise --full pour supprimer aussi les stacks)"
fi
echo "════════════════════════════════════════════════════════"
echo ""

# ─── Suppression des Ingress ──────────────────────────────────────────────────
echo "▶ Suppression des Ingress..."

$KUBE delete ingress argocd-ingress      -n argocd       --ignore-not-found
ok "Ingress argocd.local supprimé"

$KUBE delete ingress linkerd-viz-ingress -n linkerd-viz  --ignore-not-found
ok "Ingress linkerd.local supprimé"

$KUBE delete ingress grafana-ingress     -n monitoring   --ignore-not-found
ok "Ingress grafana.local supprimé"

$KUBE delete ingress prometheus-ingress  -n monitoring   --ignore-not-found
ok "Ingress prometheus.local supprimé"

# ─── Restauration Linkerd web (enforced-host strict) ─────────────────────────
echo ""
echo "▶ Restauration de l'enforced-host Linkerd Viz..."
if $KUBE get deployment web -n linkerd-viz &>/dev/null; then
  $KUBE patch deployment web -n linkerd-viz --type=json \
    -p='[{"op":"replace","path":"/spec/template/spec/containers/0/args/5",
         "value":"-enforced-host=^(localhost|127\\.0\\.0\\.1|web\\.linkerd-viz\\.svc\\.cluster\\.local|web\\.linkerd-viz\\.svc|\\[::1\\])(:\\d+)?$"}]' \
    2>/dev/null || true
  ok "enforced-host restauré (localhost uniquement)"
fi

if ! $FULL_UNINSTALL; then
  echo ""
  echo "════════════════════════════════════════════════════════"
  echo "  Ingress supprimés. Les stacks sont conservées."
  echo "  Pour tout supprimer : sudo bash uninstall-all.sh --full"
  echo "════════════════════════════════════════════════════════"
  exit 0
fi

# ─── Désinstallation complète (--full) ───────────────────────────────────────
echo ""
echo "▶ Désinstallation kube-prometheus-stack..."
if helm status kube-prometheus-stack -n monitoring &>/dev/null; then
  helm uninstall kube-prometheus-stack -n monitoring
  ok "kube-prometheus-stack désinstallé"
else
  warn "kube-prometheus-stack non trouvé via Helm"
fi

echo ""
echo "▶ Désinstallation ArgoCD..."
if $KUBE get namespace argocd &>/dev/null; then
  $KUBE delete namespace argocd
  ok "namespace argocd supprimé"
fi

echo ""
echo "▶ Suppression namespace monitoring..."
if $KUBE get namespace monitoring &>/dev/null; then
  $KUBE delete namespace monitoring
  ok "namespace monitoring supprimé"
fi

echo ""
echo "▶ Retrait annotation Linkerd sur distributed-app..."
$KUBE annotate namespace distributed-app linkerd.io/inject- --overwrite 2>/dev/null || true
ok "Annotation linkerd.io/inject retirée"

echo ""
echo "════════════════════════════════════════════════════════"
echo "  Désinstallation complète terminée."
echo "  Linkerd et Flagger sont conservés (désinstallation"
echo "  manuelle via linkerd uninstall | kubectl delete -f -)"
echo "════════════════════════════════════════════════════════"
