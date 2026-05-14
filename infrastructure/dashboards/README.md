# Dashboards d'observation du cluster

Stack d'observabilité déployée sur k3s (WSL2) pour le projet de mémoire :
**Déploiement continu Zero-Downtime via GitOps + Canary (Flagger/Linkerd).**

---

## Accès rapide

| Outil | URL | Identifiants | Rôle |
|---|---|---|---|
| ArgoCD | http://argocd.local | `admin` / voir ci-dessous | GitOps — sync Git ↔ Cluster |
| Linkerd Viz | http://linkerd.local | *(pas d'auth en dev)* | Canary — service mesh + métriques |
| Grafana | http://grafana.local | `admin` / voir ci-dessous | Métriques custom + dashboards |
| Prometheus | http://prometheus.local | *(pas d'auth)* | Source de vérité métriques |

---

## 🌐 Accéder à l'application e-commerce

### Lancer l'application

```powershell
cd C:\Users\LOQ\Desktop\distributed-app\infrastructure\dashboards\scripts
.\start-app.ps1
```

### URLs disponibles

| Service | URL | Description |
|---|---|---|
| Frontend | http://localhost:3000 | Interface React (ÉLYSE PARFUMS) |
| Auth Service | http://localhost:8001 | API Authentification & JWT |
| Products Service | http://localhost:8002 | API Catalogue produits |
| Orders Service | http://localhost:8003 | API Commandes & panier |
| Payment Service | http://localhost:8004 | API Paiements & transactions |
| Interation Service | http://localhost:8005 | API Avis & notation produits |

### Pourquoi port-forward et pas Ingress ?

Sur WSL2 en mode **mirrored networking**, Windows ne peut pas atteindre les
ports en écoute dans WSL2 directement (limitation Hyper-V / NAT).
Les Ingress Traefik fonctionnent depuis WSL2 lui-même mais pas depuis Chrome
côté Windows. La solution `kubectl port-forward` contourne cette limitation
en créant des tunnels `localhost` côté Windows.

> Les Ingress restent configurés et seraient utilisés en production.

### Arrêter l'application

```powershell
.\infrastructure\dashboards\scripts\stop-all.ps1
```

---

## 🔁 Routine de travail quotidienne

1. Allumer le PC et lancer VS Code sur le projet
2. Dans un terminal PowerShell (racine du projet) :

   ```powershell
   .\infrastructure\dashboards\scripts\start-everything.ps1
   ```

   Ce script lance en une seule commande :
   - ArgoCD → http://localhost:8080
   - Grafana → http://localhost:8081
   - Prometheus → http://localhost:8082
   - Linkerd Viz → http://localhost:8083
   - Frontend → http://localhost:3000
   - Les 5 microservices → http://localhost:8001 à 8005

3. Travailler (développement, tests, observation des déploiements canary)
4. À la fin de la session :

   ```powershell
   .\infrastructure\dashboards\scripts\stop-all.ps1
   ```

### Idempotence

Relancer `start-app.ps1` ou `start-everything.ps1` tue proprement les
anciens port-forwards avant d'en ouvrir de nouveaux — aucune action
manuelle requise entre deux sessions.

---

## Prérequis — Fichier hosts Windows

Ouvrir `C:\Windows\System32\drivers\etc\hosts` **en tant qu'Administrateur**
(clic droit → Notepad → Exécuter en tant qu'administrateur) et ajouter :

```
127.0.0.1   argocd.local linkerd.local grafana.local prometheus.local
```

> **Note WSL2 mirrored networking :** si `wsl --version` indique le mode
> mirrored, `127.0.0.1` fonctionne directement depuis Windows.
> Sinon, remplacer par l'IP retournée par :
> ```powershell
> wsl -d Ubuntu -u root -e bash -c "k3s kubectl get svc traefik -n kube-system -o jsonpath='{.status.loadBalancer.ingress[0].ip}'"
> ```

---

## Récupérer les mots de passe

### ArgoCD

```bash
# Depuis WSL Ubuntu (en root)
k3s kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d && echo
```

### Grafana

```bash
# Depuis WSL Ubuntu (en root)
k3s kubectl get secret kube-prometheus-stack-grafana \
  -n monitoring -o jsonpath='{.data.admin-password}' | base64 -d && echo
```

---

## Architecture — Flagger + Linkerd (Canary)

```
 Développeur
     │ git push
     ▼
 GitHub Actions (CI)
  ├── tests + build image Docker
  └── push tag → gitops-repo (bump image tag)
     │
     ▼
 ArgoCD détecte le changement dans gitops-repo
     │ kubectl apply
     ▼
 Flagger (Canary CRD dans distributed-app)
  ├── crée un Service "canary" (ex: auth-service-canary)
  ├── route 5% du trafic → pods canary
  │       │
  │   Linkerd proxy (sidecar injecté)
  │       │ métriques : success rate, latence p99
  │       ▼
  │   linkerd-viz/prometheus (scrape les proxies)
  │       │
  │   Flagger analyse (AnalysisRun)
  │       ├── success rate ≥ 99% ? → promotion +20%
  │       └── échec ?              → rollback automatique
  │
  └── 5% → 25% → 50% → 100% → promotion complète
```

**Flagger lit les métriques depuis** `prometheus.linkerd-viz.svc.cluster.local:9090`,
qui scrape les proxies Linkerd injectés dans chaque pod de `distributed-app`.

### Ports des services internes

| Service | Namespace | Port |
|---|---|---|
| `argocd-server` | `argocd` | 80 (insecure) |
| `web` (Linkerd Viz) | `linkerd-viz` | 8084 |
| `kube-prometheus-stack-grafana` | `monitoring` | 80 |
| `kube-prometheus-stack-prometheus` | `monitoring` | 9090 |

---

## Scripts d'installation

```bash
# Depuis WSL Ubuntu — installation complète (idempotente)
sudo bash /mnt/c/Users/LOQ/Desktop/distributed-app/infrastructure/dashboards/install-all.sh

# Supprimer uniquement les Ingress
sudo bash /mnt/c/Users/LOQ/Desktop/distributed-app/infrastructure/dashboards/uninstall-all.sh

# Supprimer toute la stack (ArgoCD + Monitoring)
sudo bash /mnt/c/Users/LOQ/Desktop/distributed-app/infrastructure/dashboards/uninstall-all.sh --full
```

---

## Vérifications rapides

```bash
# État de tous les pods des dashboards
k3s kubectl get pods -n argocd
k3s kubectl get pods -n linkerd
k3s kubectl get pods -n linkerd-viz
k3s kubectl get pods -n monitoring

# Tous les Ingress d'un coup
k3s kubectl get ingress -A

# Injection Linkerd active sur distributed-app ?
k3s kubectl get ns distributed-app -o jsonpath='{.metadata.annotations.linkerd\.io/inject}'

# Appliquer l'injection sur les pods existants (après annotation du namespace)
k3s kubectl rollout restart deployment -n distributed-app
```

---

## Dashboards Grafana recommandés pour le mémoire

Après connexion sur http://grafana.local (menu Dashboards → Browse) :

| Dashboard | Ce qu'il montre |
|---|---|
| **Kubernetes / Compute Resources / Namespace (Pods)** | CPU + RAM des pods `distributed-app` en temps réel |
| **Kubernetes / Compute Resources / Pod** | Ressources d'un pod canary vs stable |
| **Kubernetes / Networking / Namespace (Pods)** | Trafic réseau — idéal pour voir le split 5%/95% |
| **Kubernetes / Kubelet** | Santé globale du nœud pendant le déploiement |

---

## Requêtes PromQL utiles (http://prometheus.local)

```promql
# Taux de succès HTTP par pod (via Linkerd)
sum(rate(response_total{namespace="distributed-app",classification="success"}[1m]))
  by (pod)
/
sum(rate(response_total{namespace="distributed-app"}[1m]))
  by (pod)

# Latence p99 par déploiement
histogram_quantile(0.99,
  sum(rate(response_latency_ms_bucket{namespace="distributed-app"}[1m]))
  by (le, deployment)
)

# Nombre de pods Running par namespace
count(kube_pod_status_phase{phase="Running"}) by (namespace)
```

---

## Captures recommandées pour la soutenance

1. **ArgoCD UI** → application `distributed-app` en statut **Synced / Healthy**
2. **ArgoCD UI** → historique des déploiements (onglet History)
3. **Linkerd Viz** → graphe de trafic avec le split canary visible (5% / 95%)
4. **Linkerd Viz** → progression automatique 25% → 50% → 100% (ou rollback)
5. **Grafana** → dashboard Namespace avec métriques stables pendant le Canary
6. **Grafana** → pic d'erreurs sur le canary → rollback automatique Flagger

---

## Lens Desktop — Exploration du cluster (optionnel)

Lens est une application desktop (non installable via terminal) qui permet
d'explorer le cluster Kubernetes avec une interface graphique riche.

### Téléchargement

- **Lens Desktop (officiel)** : https://k8slens.dev/
- **OpenLens (open-source, sans compte requis)** : https://github.com/MuhammedKalkan/OpenLens/releases
- **Headlamp (CNCF, léger)** : https://headlamp.dev/

> Recommandation pour ce projet : **OpenLens** (identique à Lens sans
> obligation de compte) ou **Headlamp** (plus léger, parfait pour soutenance).

### Installation sur Windows (OpenLens ou Lens)

1. Télécharger le `.exe` depuis la page releases
2. Lancer l'installateur et suivre les étapes
3. Ouvrir l'application

### Associer le cluster k3s

```powershell
# Depuis PowerShell Windows — exporter le kubeconfig de WSL
wsl -d Ubuntu -u root -e bash -c "cat /etc/rancher/k3s/k3s.yaml" `
  | Out-File -Encoding utf8 "$env:USERPROFILE\.kube\config"

# Remplacer l'adresse du serveur (127.0.0.1 → IP WSL2 si nécessaire)
# Avec mirrored networking, 127.0.0.1:6443 fonctionne directement
```

Puis dans Lens/OpenLens : **+ Add Cluster** → sélectionner
`%USERPROFILE%\.kube\config` → le cluster apparaît automatiquement.

### Headlamp (alternative légère)

```powershell
# Idem pour Headlamp — il lit le même kubeconfig
wsl -d Ubuntu -u root -e bash -c "cat /etc/rancher/k3s/k3s.yaml" `
  | Out-File -Encoding utf8 "$env:USERPROFILE\.kube\config"
```

Headlamp détecte automatiquement le kubeconfig au démarrage.
