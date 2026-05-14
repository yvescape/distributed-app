param(
    [ValidateSet("up", "down", "status")]
    [string]$Action = "up"
)

# ---------------------------------------------------------------------------
# Architecture production-like
# ---------------------------------------------------------------------------
# Toute l'application passe par UN SEUL point d'entree : Traefik (Ingress).
# Le routing interne est gere par les IngressRoutes dans le namespace
# distributed-app (gerees par ArgoCD via gitops-repo).
#
# - http://distributed-app.local:8000/           -> frontend
# - http://distributed-app.local:8000/api/*      -> microservices APIs
# - http://distributed-app.local:8000/admin/*    -> Django admin
#
# Les dashboards GitOps/observabilite gardent un port-forward dedie.
# ---------------------------------------------------------------------------

$IngressEntry = @{
    Name       = "Traefik (Application)"
    Namespace  = "kube-system"
    Svc        = "traefik"
    LocalPort  = 8000
    RemotePort = 80
}

$Dashboards = @(
    @{ Name = "ArgoCD";      Namespace = "argocd";      Svc = "argocd-server";                    LocalPort = 8080; RemotePort = 80   },
    @{ Name = "Grafana";     Namespace = "monitoring";  Svc = "kube-prometheus-stack-grafana";    LocalPort = 8081; RemotePort = 80   },
    @{ Name = "Prometheus";  Namespace = "monitoring";  Svc = "kube-prometheus-stack-prometheus"; LocalPort = 8082; RemotePort = 9090 },
    @{ Name = "Linkerd Viz"; Namespace = "linkerd-viz"; Svc = "web";                              LocalPort = 8083; RemotePort = 8084 }
)

$AllPorts = @($IngressEntry.LocalPort) + ($Dashboards | ForEach-Object { $_.LocalPort })

# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------
function Write-Step($msg) {
    Write-Host "`n>> $msg" -ForegroundColor Cyan
}

function Test-Cluster {
    $null = kubectl cluster-info
    return $LASTEXITCODE -eq 0
}

function EnsureCluster {
    if (Test-Cluster) { return $true }

    Write-Host "  [!] Cluster k3s inaccessible. Tentative de demarrage..." -ForegroundColor Yellow
    wsl -- bash -c "sudo systemctl start k3s" | Out-Null
    Start-Sleep -Seconds 15

    if (Test-Cluster) {
        Write-Host "  [OK] k3s demarre." -ForegroundColor Green
        return $true
    }
    return $false
}

function Start-PortForward($entry) {
    $conn = Get-NetTCPConnection -LocalPort $entry.LocalPort -State Listen -ErrorAction SilentlyContinue
    if ($conn) {
        $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
        if ($proc -and ($proc.Name -in @("kubectl", "wsl", "powershell", "pwsh"))) {
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            Start-Sleep -Milliseconds 300
        }
    }

    $cmd = "kubectl port-forward -n $($entry.Namespace) svc/$($entry.Svc) $($entry.LocalPort):$($entry.RemotePort) --address 0.0.0.0"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd -WindowStyle Minimized
}

# ---------------------------------------------------------------------------
#  UP
# ---------------------------------------------------------------------------
function Invoke-Up {
    if (-not (EnsureCluster)) {
        Write-Host "`n  [ERREUR] Cluster k3s inaccessible." -ForegroundColor Red
        Write-Host "  Verifiez WSL2 et k3s :" -ForegroundColor DarkGray
        Write-Host "    wsl --status" -ForegroundColor DarkGray
        Write-Host "    wsl -- bash -c 'sudo systemctl status k3s'" -ForegroundColor DarkGray
        exit 1
    }

    Write-Host "`n============================================" -ForegroundColor DarkCyan
    Write-Host "  Application (via Ingress Traefik)"         -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor DarkCyan
    Write-Step "$($IngressEntry.Name) -> http://distributed-app.local:$($IngressEntry.LocalPort)"
    Start-PortForward $IngressEntry

    Write-Host "`n============================================" -ForegroundColor DarkCyan
    Write-Host "  Dashboards (GitOps / observabilite)"       -ForegroundColor Magenta
    Write-Host "============================================" -ForegroundColor DarkCyan
    foreach ($d in $Dashboards) {
        Write-Step "$($d.Name) -> http://localhost:$($d.LocalPort)"
        Start-PortForward $d
    }

    Start-Sleep -Seconds 2

    Write-Host "`n============================================" -ForegroundColor DarkCyan
    Write-Host "  URLs disponibles"                           -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor DarkCyan
    Write-Host ""
    Write-Host "  APPLICATION (point d'entree unique via Traefik)" -ForegroundColor White
    Write-Host "  -------------------------------------------------"
    Write-Host "    Frontend     : http://distributed-app.local:8000/"              -ForegroundColor White
    Write-Host "    API Auth     : http://distributed-app.local:8000/api/auth/"     -ForegroundColor Gray
    Write-Host "    API Products : http://distributed-app.local:8000/api/products/" -ForegroundColor Gray
    Write-Host "    API Orders   : http://distributed-app.local:8000/api/orders/"   -ForegroundColor Gray
    Write-Host "    API Payments : http://distributed-app.local:8000/api/payments/" -ForegroundColor Gray
    Write-Host "    API Reviews  : http://distributed-app.local:8000/api/interation/" -ForegroundColor Gray
    Write-Host "    Admin        : http://distributed-app.local:8000/admin/auth/"   -ForegroundColor Gray
    Write-Host ""
    Write-Host "  DASHBOARDS" -ForegroundColor White
    Write-Host "  ----------"
    Write-Host "    ArgoCD       : http://localhost:8080  (admin / argocd-initial-admin-secret)" -ForegroundColor White
    Write-Host "    Grafana      : http://localhost:8081  (admin / prom-operator)"               -ForegroundColor White
    Write-Host "    Prometheus   : http://localhost:8082"                                         -ForegroundColor White
    Write-Host "    Linkerd Viz  : http://localhost:8083"                                         -ForegroundColor White
    Write-Host ""
    Write-Host "  Pour arreter : .\start.ps1 -Action down" -ForegroundColor DarkGray
    Write-Host "`n=== Environnement demarre ===" -ForegroundColor Green
}

# ---------------------------------------------------------------------------
#  DOWN
# ---------------------------------------------------------------------------
function Invoke-Down {
    Write-Host "`n============================================" -ForegroundColor DarkCyan
    Write-Host "  Arret des port-forwards"                   -ForegroundColor Yellow
    Write-Host "============================================" -ForegroundColor DarkCyan

    $killed = 0
    foreach ($port in $AllPorts) {
        $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        if ($conn) {
            $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
            if ($proc -and ($proc.Name -in @("kubectl", "wsl", "powershell", "pwsh"))) {
                Write-Step "Arret port $port (PID $($proc.Id) - $($proc.Name))"
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
                $killed++
            }
        }
    }

    if ($killed -eq 0) {
        Write-Host "  Aucun port-forward actif." -ForegroundColor DarkGray
    } else {
        Write-Host "`n  $killed port-forward(s) arretes." -ForegroundColor Green
    }

    Write-Host "`n=== Arret termine ===" -ForegroundColor Yellow
}

# ---------------------------------------------------------------------------
#  STATUS
# ---------------------------------------------------------------------------
function Invoke-Status {
    Write-Host "`n============================================" -ForegroundColor DarkCyan
    Write-Host "  Pods k3s (namespace distributed-app)"      -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor DarkCyan
    kubectl get pods -n distributed-app -o wide

    Write-Host "`n============================================" -ForegroundColor DarkCyan
    Write-Host "  Applications ArgoCD"                        -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor DarkCyan
    kubectl get applications -n argocd

    Write-Host "`n============================================" -ForegroundColor DarkCyan
    Write-Host "  Canaries Flagger"                           -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor DarkCyan
    kubectl get canaries.flagger.app -n distributed-app

    Write-Host "`n============================================" -ForegroundColor DarkCyan
    Write-Host "  Port-forwards actifs"                       -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor DarkCyan

    $all = @($IngressEntry) + $Dashboards
    foreach ($entry in $all) {
        $conn = Get-NetTCPConnection -LocalPort $entry.LocalPort -State Listen -ErrorAction SilentlyContinue
        if ($conn) {
            $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
            $pname = if ($proc) { $proc.Name } else { "?" }
            Write-Host "  [OK]  $($entry.Name.PadRight(22)) localhost:$($entry.LocalPort)  (PID $($conn.OwningProcess) - $pname)" -ForegroundColor Green
        } else {
            Write-Host "  [--]  $($entry.Name.PadRight(22)) localhost:$($entry.LocalPort)  inactif" -ForegroundColor DarkGray
        }
    }

    Write-Host ""
}

# ---------------------------------------------------------------------------
#  Dispatch
# ---------------------------------------------------------------------------
switch ($Action) {
    "up"     { Invoke-Up }
    "down"   { Invoke-Down }
    "status" { Invoke-Status }
}