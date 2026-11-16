#!/usr/bin/env bash
# Krok 5: centralne logi i telemetria. Bezpieczne do ponownego uruchomienia.
# - ustawia limit dzienny i retencję w obszarze Log Analytics, do którego już trafiają logi kontenerów,
# - tworzy Application Insights (czas odpowiedzi API, błędy, zapytania do bazy) i podłącza go do back-endu,
# - kieruje logi serwera PostgreSQL do tego samego obszaru.
set -euo pipefail
cd "$(dirname "$0")"
# shellcheck source=/dev/null
source ./vars.sh
ENV_NAME="${ENV_NAME:-cae-main}"
APPI_NAME="${APPI_NAME:-appi-model-manager}"
LOG_DAILY_CAP_GB="${LOG_DAILY_CAP_GB:-1}"
LOCATION=$(az group show --name "$RG" --query location -o tsv)

echo "1/5 Obszar roboczy Log Analytics środowiska Container Apps"
WORKSPACE_CUSTOMER_ID=$(az containerapp env show --name "$ENV_NAME" --resource-group "$RG" \
  --query properties.appLogsConfiguration.logAnalyticsConfiguration.customerId -o tsv)
WORKSPACE_ID=$(az monitor log-analytics workspace list --resource-group "$RG" \
  --query "[?customerId=='${WORKSPACE_CUSTOMER_ID}'].id | [0]" -o tsv)
if [ -z "$WORKSPACE_ID" ]; then
  echo "BŁĄD: nie znaleziono obszaru Log Analytics środowiska $ENV_NAME w grupie $RG" >&2
  exit 1
fi
WORKSPACE_NAME=$(basename "$WORKSPACE_ID")
echo "   Obszar: $WORKSPACE_NAME"

echo "2/5 Limit dzienny ${LOG_DAILY_CAP_GB} GB i retencja 30 dni (ochrona budżetu)"
az monitor log-analytics workspace update --resource-group "$RG" --workspace-name "$WORKSPACE_NAME" \
  --quota "$LOG_DAILY_CAP_GB" --retention-time 30 --output none

echo "3/5 Application Insights ($APPI_NAME), powiązany z tym samym obszarem"
az extension add --name application-insights --upgrade --only-show-errors
if ! az monitor app-insights component show --app "$APPI_NAME" --resource-group "$RG" > /dev/null 2>&1; then
  az monitor app-insights component create --app "$APPI_NAME" --location "$LOCATION" --resource-group "$RG" \
    --workspace "$WORKSPACE_ID" --kind web --application-type web --output none
fi
CONNECTION_STRING=$(az monitor app-insights component show --app "$APPI_NAME" --resource-group "$RG" \
  --query connectionString -o tsv)

echo "4/5 Back-end: connection string jako sekret i zmienna środowiskowa (powstaje nowa rewizja)"
az containerapp secret set --name "$BACKEND_APP" --resource-group "$RG" \
  --secrets "appinsights-connection-string=${CONNECTION_STRING}" --output none
az containerapp update --name "$BACKEND_APP" --resource-group "$RG" \
  --set-env-vars "APPLICATIONINSIGHTS_CONNECTION_STRING=secretref:appinsights-connection-string" --output none

echo "5/5 Logi serwera PostgreSQL do tego samego obszaru"
PG_ID=$(az postgres flexible-server show --resource-group "$RG" --name "$PG_SERVER" --query id -o tsv)
log_categories=$(az monitor diagnostic-settings categories list --resource "$PG_ID" --query "[?categoryType=='Logs'].name" -o tsv)
if grep -qx "PostgreSQLLogs" <<< "$log_categories"; then
  az monitor diagnostic-settings create --name diag-postgres --resource "$PG_ID" --workspace "$WORKSPACE_ID" \
    --logs '[{"category":"PostgreSQLLogs","enabled":true}]' \
    --metrics '[{"category":"AllMetrics","enabled":true}]' --output none
else
  echo "UWAGA: kategoria PostgreSQLLogs nie jest dostępna dla tego serwera. Dostępne kategorie logów:"
  echo "$log_categories"
fi
# Zapytania wolniejsze niż 1 sekunda trafiają do logów serwera
az postgres flexible-server parameter set --resource-group "$RG" --server-name "$PG_SERVER" \
  --name log_min_duration_statement --value 1000 --output none

echo ""
echo "Gotowe. Dane pojawiają się w Log Analytics i Application Insights po kilku minutach."
echo "Przykładowe zapytania i konfiguracja dashboardu: docs/deployment.md (krok H)."
