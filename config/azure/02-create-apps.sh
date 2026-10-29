#!/usr/bin/env bash
# Krok 2: utworzenie aplikacji kontenerowych. Uruchom po 01-provision.sh ORAZ po pierwszym przebiegu
# workflow CD (ręczne uruchomienie), który wysyła obrazy do rejestru.
# Sekrety są podawane interaktywnie: nie trafiają do plików, historii poleceń ani do repozytorium.
set -euo pipefail
cd "$(dirname "$0")"
# shellcheck source=/dev/null
source ./vars.sh

REGISTRY="${ACR_NAME}.azurecr.io"
STORAGE_URL=$(az storage account show --resource-group "$RG" --name "$STORAGE_ACCOUNT" --query primaryEndpoints.blob -o tsv)
STORAGE_URL="${STORAGE_URL%/}"

echo "Obrazy w rejestrze (powinny być oba, wysłane przez workflow CD):"
az acr repository list --name "$ACR_NAME" -o tsv

read -rp "Użytkownik PostgreSQL: " PG_USER
read -rsp "Hasło PostgreSQL: " PG_PASSWORD; echo
read -rp "E-mail pierwszego administratora aplikacji: " ADMIN_EMAIL
read -rsp "Hasło administratora aplikacji (min. 8 znaków, litera i cyfra): " ADMIN_PASSWORD; echo

# Znaki specjalne w haśle muszą być zakodowane w adresie połączenia
PG_PASSWORD_ENCODED=$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.stdin.read().strip(), safe=""))' <<< "$PG_PASSWORD")
DATABASE_URL="postgresql+psycopg://${PG_USER}:${PG_PASSWORD_ENCODED}@${PG_SERVER_FQDN}:5432/${PG_DB}?sslmode=require"
JWT_SECRET=$(openssl rand -base64 48 | tr -d '\n=+/')

BACKEND_IDENTITY_ID=$(az identity show --resource-group "$RG" --name id-backend --query id -o tsv)
BACKEND_CLIENT_ID=$(az identity show --resource-group "$RG" --name id-backend --query clientId -o tsv)
FRONTEND_IDENTITY_ID=$(az identity show --resource-group "$RG" --name id-frontend --query id -o tsv)

echo "Back-end (środowisko wewnętrzne, podsieć prywatna)"
# - jedna replika: migracje bazy uruchamiają się przy starcie kontenera i nie powinny działać równolegle
# - AZURE_CLIENT_ID wskazuje tożsamość, której aplikacja używa do magazynu plików
# - ruch HTTP jest dozwolony, bo front-end łączy się z back-endem wewnątrz sieci wirtualnej
az containerapp create --name "$BACKEND_APP" --resource-group "$RG" --environment "$ENV_APP" \
  --image "${REGISTRY}/model-manager-backend:latest" \
  --user-assigned "$BACKEND_IDENTITY_ID" \
  --registry-server "$REGISTRY" --registry-identity "$BACKEND_IDENTITY_ID" \
  --ingress internal --target-port 8000 --allow-insecure true \
  --min-replicas 1 --max-replicas 1 --cpu 0.5 --memory 1.0Gi \
  --secrets "database-url=${DATABASE_URL}" "jwt-secret=${JWT_SECRET}" "admin-password=${ADMIN_PASSWORD}" \
  --env-vars "DATABASE_URL=secretref:database-url" "JWT_SECRET=secretref:jwt-secret" \
    "ADMIN_EMAIL=${ADMIN_EMAIL}" "ADMIN_PASSWORD=secretref:admin-password" \
    "APP_ENV=production" "STORAGE_ACCOUNT_URL=${STORAGE_URL}" "STORAGE_CONTAINER=models" \
    "MAX_UPLOAD_MB=200" "AZURE_CLIENT_ID=${BACKEND_CLIENT_ID}" \
  --output none

BACKEND_FQDN=$(az containerapp show --name "$BACKEND_APP" --resource-group "$RG" --query properties.configuration.ingress.fqdn -o tsv)
echo "Adres wewnętrzny back-endu: $BACKEND_FQDN"

echo "Front-end (środowisko z publicznym adresem, podsieć publiczna)"
az containerapp create --name "$FRONTEND_APP" --resource-group "$RG" --environment "$ENV_WEB" \
  --image "${REGISTRY}/model-manager-frontend:latest" \
  --user-assigned "$FRONTEND_IDENTITY_ID" \
  --registry-server "$REGISTRY" --registry-identity "$FRONTEND_IDENTITY_ID" \
  --ingress external --target-port 80 \
  --min-replicas 1 --max-replicas 2 --cpu 0.25 --memory 0.5Gi \
  --env-vars "BACKEND_URL=http://${BACKEND_FQDN}" \
  --output none

PUBLIC_FQDN=$(az containerapp show --name "$FRONTEND_APP" --resource-group "$RG" --query properties.configuration.ingress.fqdn -o tsv)
echo ""
echo "Gotowe. Publiczny adres aplikacji: https://${PUBLIC_FQDN}"
echo "Ustaw w GitHubie zmienną repozytorium PUBLIC_URL = https://${PUBLIC_FQDN}"
