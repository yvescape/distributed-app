#!/usr/bin/env bash
# install-all.sh — Installation idempotente des dashboards d'observation
# Stack : ArgoCD + Linkerd Viz + Grafana + Prometheus (Flagger/Linkerd)
# Prérequis : k3s actif dans WSL2, exécuter en root ou avec sudo
# Usage   : sudo bash install-all.sh

set -euo pipefail

# ─── Couleurs ────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✅ $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }
info() { echo -e "   $*"; }

# ─── Configuration ────────────────────────────────────────────────────────────
ARGOCD_VERSION="v3.3.6"
INGRESS_DIR="$(cd "$(dirname "$0")/ingress" && pwd)"
KUBE="k3s kubectl"

echo "════════════════════════════════════════════════════════"
echo "  Installation des dashboards — cluster k3s (WSL2)"
echo "════════════════════════════════════════════════════════"

# ─── ÉTAPE 0 : Prérequis ─────────────────────────────────────────────────────
echo ""
echo "▶ Vérification des prérequis..."

if ! command -v k3s &>/dev/null; then
  echo -e "${RED}❌ k3s introuvable. Installe k3s et relance ce script.${NC}"
  exit 1
fi
ok "k3s $(k3s --version | head -1)"

if ! command -v helm &>/dev/null; then
  warn "helm introuvable — installation automatique..."
  curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
  ok "Helm installé : $(helm version --short)"
else
  ok "Helm $(helm version --short)"
fi

if ! $KUBE get nodes &>/dev/null; then
  echo -e "${RED}❌ Impossible de joindre le cluster. Vérifie que k3s est actif (systemctl status k3s).${NC}"
  exit 1
fi
NODE_STATUS=$($KUBE get nodes --no-headers | awk '{print $2}')
if [ "$NODE_STATUS" != "Ready" ]; then
  echo -e "${RED}❌ Le nœud n'est pas Ready : $NODE_STATUS${NC}"
  exit 1
fi
ok "Cluster k3s opérationnel ($($KUBE get nodes --no-headers | awk '{print $1}'))"

# ─── ÉTAPE 1 : Namespaces ────────────────────────────────────────────────────
echo ""
echo "▶ Création des namespaces..."

for ns in argocd monitoring; do
  if $KUBE get namespace "$ns" &>/dev/null; then
    info "namespace/$ns déjà présent"
  else
    $KUBE create namespace "$ns"
    ok "namespace/$ns créé"
  fi
done

# distributed-app : annoter pour Linkerd injection
if $KUBE get namespace distributed-app &>/dev/null; then
  $KUBE annotate namespace distributed-app linkerd.io/inject=enabled --overwrite
  ok "namespace/distributed-app annoté (linkerd.io/inject=enabled)"
else
  warn "namespace/distributed-app absent — création et annotation"
  $KUBE create namespace distributed-app
  $KUBE annotate namespace distributed-app linkerd.io/inject=enabled
  ok "namespace/distributed-app créé et annoté"
fi

# ─── ÉTAPE 2 : ArgoCD ────────────────────────────────────────────────────────
echo ""
echo "▶ Installation ArgoCD ${ARGOCD_VERSION}..."

ARGOCD_URL="https://raw.githubusercontent.com/argoproj/argo-cd/${ARGOCD_VERSION}/manifests/install.yaml"
ARGOCD_CRD_URL="https://raw.githubusercontent.com/argoproj/argo-cd/${ARGOCD_VERSION}/manifests/crds/applicationset-crd.yaml"

if $KUBE get deployment argocd-server -n argocd &>/dev/null; then
  info "ArgoCD déjà installé — vérification des CRDs manquants..."
else
  $KUBE apply --server-side -f "$ARGOCD_URL"
  ok "ArgoCD installé"
fi

# Restaurer le CRD ApplicationSet s'il manque (bug connu après upgrade)
if ! $KUBE get crd applicationsets.argoproj.io &>/dev/null; then
  warn "CRD applicationsets.argoproj.io manquant — restauration..."
  curl -fsSL "$ARGOCD_CRD_URL" | $KUBE apply --server-side -f -
  ok "CRD ApplicationSet restauré"
else
  info "CRD applicationsets.argoproj.io présent"
fi

# Mode insecure (pas de TLS en dev)
$KUBE patch configmap argocd-cmd-params-cm -n argocd \
  --type merge -p '{"data":{"server.insecure":"true"}}' 2>/dev/null || true

# Fix init container copyutil (ln -s échoue si symlink existe déjà)
CURRENT_ARG=$($KUBE get deployment argocd-repo-server -n argocd \
  -o jsonpath='{.spec.template.spec.initContainers[0].args[0]}' 2>/dev/null || echo "")
if [[ "$CURRENT_ARG" != *"ln -sf"* ]]; then
  $KUBE patch deployment argocd-repo-server -n argocd --type=json -p='[
    {"op":"replace","path":"/spec/template/spec/initContainers/0/args/0",
     "value":"/bin/cp --update=none /usr/local/bin/argocd /var/run/argocd/argocd && (ln -sf /var/run/argocd/argocd /var/run/argocd/argocd-cmp-server || true)"}
  ]' 2>/dev/null || true
  info "Patch repo-server (ln -sf) appliqué"
fi

$KUBE rollout restart deployment argocd-server -n argocd &>/dev/null || true

echo ""
info "Attente ArgoCD (max 3 min)..."
$KUBE wait --for=condition=available --timeout=180s \
  deployment/argocd-server deployment/argocd-repo-server \
  -n argocd 2>/dev/null || warn "Timeout ArgoCD — vérifie manuellement : kubectl get pods -n argocd"
ok "ArgoCD opérationnel"

# ─── ÉTAPE 3 : Linkerd + Flagger ─────────────────────────────────────────────
echo ""
echo "▶ Vérification Linkerd + Flagger..."

if $KUBE get pods -n linkerd --no-headers 2>/dev/null | grep -q "Running"; then
  ok "Linkerd control plane Running"
else
  warn "Linkerd non détecté. Installation manuelle requise :"
  info "  → https://linkerd.io/2/getting-started/"
  info "  → linkerd install --crds | kubectl apply -f -"
  info "  → linkerd install | kubectl apply -f -"
  info "  → linkerd viz install | kubectl apply -f -"
fi

if $KUBE get crd canaries.flagger.app &>/dev/null; then
  ok "Flagger CRD (canaries.flagger.app) présent"
else
  warn "Flagger non détecté. Installation manuelle requise :"
  info "  → helm repo add flagger https://flagger.app"
  info "  → helm install flagger flagger/flagger -n linkerd-viz --set meshProvider=linkerd"
fi

# Patch dashboard Linkerd Viz (enforced-host) pour accès via Ingress
if $KUBE get deployment web -n linkerd-viz &>/dev/null; then
  ENFORCED_HOST=$($KUBE get deployment web -n linkerd-viz \
    -o jsonpath='{.spec.template.spec.containers[0].args[5]}' 2>/dev/null || echo "")
  if [[ "$ENFORCED_HOST" != "-enforced-host=.*" ]]; then
    $KUBE patch deployment web -n linkerd-viz --type=json \
      -p='[{"op":"replace","path":"/spec/template/spec/containers/0/args/5","value":"-enforced-host=.*"}]' \
      2>/dev/null || true
    info "Patch Linkerd web (enforced-host) appliqué"
  else
    info "Patch Linkerd web déjà appliqué"
  fi
fi

# ─── ÉTAPE 4 : Prometheus + Grafana (kube-prometheus-stack) ──────────────────
echo ""
echo "▶ Installation kube-prometheus-stack..."

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts \
  --force-update &>/dev/null
helm repo update &>/dev/null

if helm status kube-prometheus-stack -n monitoring &>/dev/null; then
  info "kube-prometheus-stack déjà installé"
else
  helm install kube-prometheus-stack \
    prometheus-community/kube-prometheus-stack \
    -n monitoring \
    --set grafana.adminPassword='admin' \
    --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
  ok "kube-prometheus-stack installé"

  info "Attente Grafana (max 3 min)..."
  $KUBE wait --for=condition=ready pod \
    -l app.kubernetes.io/name=grafana -n monitoring --timeout=180s \
    2>/dev/null || warn "Timeout Grafana — vérifie : kubectl get pods -n monitoring"
fi
ok "Grafana + Prometheus opérationnels"

# ─── ÉTAPE 5 : Ingress ───────────────────────────────────────────────────────
echo ""
echo "▶ Application des Ingress Traefik..."

for manifest in "$INGRESS_DIR"/*.yaml; do
  $KUBE apply -f "$manifest"
done
ok "Tous les Ingress appliqués"

# ─── RÉSUMÉ FINAL ─────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════"
echo "  INSTALLATION TERMINÉE"
echo "════════════════════════════════════════════════════════"
echo ""
echo "  URLs d'accès :"
echo "    http://argocd.local      → ArgoCD UI"
echo "    http://linkerd.local     → Linkerd Viz (Canary)"
echo "    http://grafana.local     → Grafana"
echo "    http://prometheus.local  → Prometheus"
echo ""
echo "  Identifiants ArgoCD :"
ARGOCD_PASS=$($KUBE -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" 2>/dev/null | base64 -d 2>/dev/null || echo "secret introuvable")
echo "    admin / ${ARGOCD_PASS}"
echo ""
echo "  Identifiants Grafana :"
GRAFANA_PASS=$($KUBE get secret kube-prometheus-stack-grafana \
  -n monitoring -o jsonpath='{.data.admin-password}' 2>/dev/null | base64 -d 2>/dev/null || echo "admin")
echo "    admin / ${GRAFANA_PASS}"
echo ""
echo "  Fichier hosts Windows (C:\Windows\System32\drivers\etc\hosts) :"
TRAEFIK_IP=$($KUBE get svc traefik -n kube-system \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "127.0.0.1")
echo "    ${TRAEFIK_IP}   argocd.local linkerd.local grafana.local prometheus.local"
echo ""
echo "  Note : si WSL2 mirrored networking est activé, utilise 127.0.0.1"
echo "════════════════════════════════════════════════════════"
