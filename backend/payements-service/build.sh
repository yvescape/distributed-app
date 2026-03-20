#!/bin/bash
set -euo pipefail

# ── Configuration ─────────────────────────────────────────────
DOCKER_USER="capedev"
IMAGE_NAME="auth-service"
GIT_SHA=$(git rev-parse --short HEAD)
BRANCH=$(git rev-parse --abbrev-ref HEAD | tr "/" "-")
FULL_IMAGE="${DOCKER_USER}/${IMAGE_NAME}"

echo "======================================"
echo " Build : ${FULL_IMAGE}:${GIT_SHA}"
echo "======================================"

# ── Étape 1 : Build ───────────────────────────────────────────
echo ""
echo "[1/4] Build de l'image..."
docker build \
  --tag "${FULL_IMAGE}:${GIT_SHA}" \
  --tag "${FULL_IMAGE}:${BRANCH}" \
  --tag "${FULL_IMAGE}:latest" \
  .

echo "Build terminé : ${FULL_IMAGE}:${GIT_SHA}"

# ── Étape 2 : Scan Trivy ──────────────────────────────────────
echo ""
echo "[2/4] Scan des vulnérabilités (Trivy)..."

# Scan complet — affiche tout
trivy image \
  --severity LOW,MEDIUM,HIGH,CRITICAL \
  --format table \
  "${FULL_IMAGE}:${GIT_SHA}"

# Scan bloquant — arrête le script si CVE CRITICAL ou HIGH trouvée
echo ""
echo "Vérification des CVE bloquantes (HIGH, CRITICAL)..."
trivy image \
  --severity HIGH,CRITICAL \
  --exit-code 1 \
  --format table \
  "${FULL_IMAGE}:${GIT_SHA}"

echo "Scan OK — aucune CVE HIGH/CRITICAL détectée."

# ── Étape 3 : Push ────────────────────────────────────────────
echo ""
echo "[3/4] Push vers Docker Hub..."
docker push "${FULL_IMAGE}:${GIT_SHA}"
docker push "${FULL_IMAGE}:${BRANCH}"
docker push "${FULL_IMAGE}:latest"

# ── Étape 4 : Résumé ──────────────────────────────────────────
echo ""
echo "[4/4] Images publiées :"
echo "  ${FULL_IMAGE}:${GIT_SHA}   ← tag immuable (utiliser en prod)"
echo "  ${FULL_IMAGE}:${BRANCH}"
echo "  ${FULL_IMAGE}:latest"
echo ""
echo "Terminé."