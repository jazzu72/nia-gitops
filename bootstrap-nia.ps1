<#
.NIA FULL GITOPS BOOTSTRAP
Author: House of Jazzu / NIA Quantum Systems
Mode: One-click deployment
Requirements:
- PowerShell 7+
- kubectl
- flux CLI
- Azure CLI (if using AKS)
- Helm
#>

param(
    [string]$GitRepo = "https://github.com/Jazzu72/nia-gitops",
    [string]$GitBranch = "main",
    [switch]$InstallIngress,
    [switch]$InstallCerts
)

Write-Host "`n🚀 NIA GITOPS BOOTSTRAP STARTING..." -ForegroundColor Cyan

# ------------------------------
# STEP 1 — VERIFY DEPENDENCIES
# ------------------------------
$bins = @("kubectl", "flux", "helm")

foreach ($bin in $bins) {
    if (-not (Get-Command $bin -ErrorAction SilentlyContinue)) {
        Write-Host "❌ Missing dependency: $bin" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✔ All dependencies installed" -ForegroundColor Green

# ------------------------------
# STEP 2 — VERIFY K8S CONNECTION
# ------------------------------
Write-Host "`n🔍 Checking kubectl cluster access..."

try {
    kubectl get nodes
} catch {
    Write-Host "❌ No Kubernetes cluster detected. Fix kubeconfig." -ForegroundColor Red
    exit 1
}

Write-Host "✔ Connected to Kubernetes cluster" -ForegroundColor Green

# ------------------------------
# STEP 3 — INSTALL FLUXCD
# ------------------------------
Write-Host "`n📦 Installing FluxCD..."

flux install --components-extra=image-reflector-controller,image-automation-controller

Write-Host "✔ FluxCD installed" -ForegroundColor Green

# ------------------------------
# STEP 4 — CONNECT FLUX TO GITHUB
# ------------------------------
Write-Host "`n🔗 Connecting Flux to GitHub repo..."

flux create source git nia-gitops `
  --url=$GitRepo `
  --branch=$GitBranch `
  --interval=1m

flux create kustomization nia-gitops `
  --source=nia-gitops `
  --path="./clusters/aks" `
  --prune=true `
  --interval=2m

Write-Host "✔ FluxCD now watches $GitRepo" -ForegroundColor Green

# ------------------------------
# OPTIONAL — INSTALL INGRESS
# ------------------------------
if ($InstallIngress) {
    Write-Host "`n🌐 Installing NGINX ingress..."

    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo update

    helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx `
      --namespace ingress-nginx `
      --create-namespace

    Write-Host "✔ NGINX ingress installed" -ForegroundColor Green
}

# ------------------------------
# OPTIONAL — INSTALL CERT-MANAGER
# ------------------------------
if ($InstallCerts) {
    Write-Host "`n🔐 Installing cert-manager..."

    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml

    Write-Host "✔ cert-manager installed" -ForegroundColor Green
}

# ------------------------------
# STEP 5 — INSTALL SEALED SECRETS
# ------------------------------
Write-Host "`n🔑 Installing SealedSecrets..."

kubectl create namespace sealed-secrets --dry-run=client -o yaml | kubectl apply -f -

helm repo add sealed-secrets https://bitnami-labs.github.io/sealed-secrets
helm repo update

helm upgrade --install sealed-secrets sealed-secrets/sealed-secrets `
  --namespace sealed-secrets

Write-Host "✔ SealedSecrets installed" -ForegroundColor Green

# ------------------------------
# STEP 6 — CONFIRM EVERYTHING
# ------------------------------
Write-Host "`n🔄 Verifying Controllers..."

kubectl get deployments -n flux-system
kubectl get deployments -n sealed-secrets

# ------------------------------
# STEP 7 — INITIAL FLUX SYNC
# ------------------------------
Write-Host "`n🔁 Triggering sync..."

flux reconcile kustomization nia-gitops --with-source

# ------------------------------
# SUCCESS MESSAGE
# ------------------------------
Write-Host "`n🎉 NIA GITOPS BOOTSTRAP COMPLETE!" -ForegroundColor Green
Write-Host "Flux is now watching: $GitRepo ($GitBranch)"
Write-Host "Your cluster will auto-update from Git." -ForegroundColor Cyan
