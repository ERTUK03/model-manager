#!/usr/bin/env bash
# Krok 1: infrastruktura (bez aplikacji). Bezpieczne do ponownego uruchomienia.
# Tworzy: rejestr kontenerów, konto magazynu, tożsamości zarządzane z uprawnieniami,
# poświadczenie OIDC dla GitHub Actions, dwa środowiska Container Apps i prywatny DNS.
set -euo pipefail
cd "$(dirname "$0")"
# shellcheck source=/dev/null
source ./vars.sh

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
TENANT_ID=$(az account show --query tenantId -o tsv)
LOCATION=$(az group show --name "$RG" --query location -o tsv)
RG_ID=$(az group show --name "$RG" --query id -o tsv)

echo "1/8 Rejestracja dostawców zasobów i rozszerzenie containerapp"
for namespace in Microsoft.App Microsoft.ContainerRegistry Microsoft.OperationalInsights \
  Microsoft.Storage Microsoft.ManagedIdentity Microsoft.Network; do
  az provider register --namespace "$namespace" --wait
done
az extension add --name containerapp --upgrade --only-show-errors

echo "2/8 Rejestr kontenerów ($ACR_NAME)"
az acr create --resource-group "$RG" --name "$ACR_NAME" --location "$LOCATION" \
  --sku Basic --admin-enabled false --only-show-errors --output none
ACR_ID=$(az acr show --name "$ACR_NAME" --query id -o tsv)

echo "3/8 Konto magazynu na pliki modeli ($STORAGE_ACCOUNT)"
az storage account create --resource-group "$RG" --name "$STORAGE_ACCOUNT" --location "$LOCATION" \
  --sku Standard_LRS --kind StorageV2 --allow-blob-public-access false --min-tls-version TLS1_2 \
  --only-show-errors --output none
STORAGE_ID=$(az storage account show --resource-group "$RG" --name "$STORAGE_ACCOUNT" --query id -o tsv)

echo "4/8 Tożsamości zarządzane i uprawnienia (zasada minimum uprawnień)"
for identity in id-backend id-frontend id-github-deploy; do
  az identity create --resource-group "$RG" --name "$identity" --location "$LOCATION" --output none
done
principal() { az identity show --resource-group "$RG" --name "$1" --query principalId -o tsv; }
assign() { # tożsamość, rola, zakres
  az role assignment create --assignee-object-id "$(principal "$1")" --assignee-principal-type ServicePrincipal \
    --role "$2" --scope "$3" --only-show-errors --output none
}
assign id-backend "AcrPull" "$ACR_ID"
assign id-backend "Storage Blob Data Contributor" "$STORAGE_ID"
assign id-backend "Storage Blob Delegator" "$STORAGE_ID"
assign id-frontend "AcrPull" "$ACR_ID"
assign id-github-deploy "Contributor" "$RG_ID"
assign id-github-deploy "AcrPush" "$ACR_ID"

echo "5/8 Poświadczenie federacyjne OIDC: GitHub Actions (środowisko production) bez haseł"
az identity federated-credential create --resource-group "$RG" --identity-name id-github-deploy \
  --name github-production --issuer "https://token.actions.githubusercontent.com" \
  --subject "repo:${GITHUB_REPO}:environment:production" --audiences "api://AzureADTokenExchange" --output none

echo "6/8 Środowiska Container Apps w podsieciach"
SUBNET_APP_ID=$(az network vnet subnet show --resource-group "$RG" --vnet-name "$VNET" --name "$SUBNET_APP" --query id -o tsv)
SUBNET_WEB_ID=$(az network vnet subnet show --resource-group "$RG" --vnet-name "$VNET" --name "$SUBNET_WEB" --query id -o tsv)
# Back-end: środowisko wewnętrzne (bez publicznego adresu)
az containerapp env create --name "$ENV_APP" --resource-group "$RG" --location "$LOCATION" \
  --infrastructure-subnet-resource-id "$SUBNET_APP_ID" --internal-only --output none
# Front-end: środowisko z publicznym adresem
az containerapp env create --name "$ENV_WEB" --resource-group "$RG" --location "$LOCATION" \
  --infrastructure-subnet-resource-id "$SUBNET_WEB_ID" --output none

echo "7/8 Prywatny DNS dla środowiska wewnętrznego (żeby front-end znalazł back-end)"
APP_DOMAIN=$(az containerapp env show --name "$ENV_APP" --resource-group "$RG" --query properties.defaultDomain -o tsv)
APP_IP=$(az containerapp env show --name "$ENV_APP" --resource-group "$RG" --query properties.staticIp -o tsv)
az network private-dns zone create --resource-group "$RG" --name "$APP_DOMAIN" --output none
az network private-dns link vnet create --resource-group "$RG" --name link-model-manager \
  --zone-name "$APP_DOMAIN" --virtual-network "$VNET" --registration-enabled false --output none
az network private-dns record-set a add-record --resource-group "$RG" --zone-name "$APP_DOMAIN" \
  --record-set-name "*" --ipv4-address "$APP_IP" --output none
az network private-dns record-set a add-record --resource-group "$RG" --zone-name "$APP_DOMAIN" \
  --record-set-name "@" --ipv4-address "$APP_IP" --output none

echo "8/8 Gotowe. Ustaw teraz wartości w GitHubie (Settings -> Secrets and variables -> Actions):"
echo ""
echo "  Secrets (Repository secrets):"
echo "    AZURE_CLIENT_ID        = $(az identity show --resource-group "$RG" --name id-github-deploy --query clientId -o tsv)"
echo "    AZURE_TENANT_ID        = $TENANT_ID"
echo "    AZURE_SUBSCRIPTION_ID  = $SUBSCRIPTION_ID"
echo ""
echo "  Variables (Repository variables):"
echo "    ACR_NAME               = $ACR_NAME"
echo "    AZURE_RESOURCE_GROUP   = $RG"
echo "    BACKEND_APP_NAME       = $BACKEND_APP"
echo "    FRONTEND_APP_NAME      = $FRONTEND_APP"
echo "    PUBLIC_URL             = (ustawisz po kroku 02-create-apps.sh)"
echo ""
echo "  Utwórz też środowisko GitHub o nazwie: production (Settings -> Environments)."
