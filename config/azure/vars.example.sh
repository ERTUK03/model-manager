# shellcheck shell=bash
# Skopiuj ten plik jako vars.sh (jest w .gitignore) i uzupełnij wartości.
# Skrypty uruchamiaj w Azure Cloud Shell (Bash) albo lokalnie po `az login`.

# Region (taki sam dla wszystkich zasobów). Sprawdź, które regiony pozwala użyć subskrypcja studencka
export LOCATION="swedencentral"
export RG="rg-model-manager"

# Sieć: jedna sieć wirtualna z trzema podsieciami
export VNET="vnet-model-manager"
export SUBNET_WEB="snet-web"
export SUBNET_APP="snet-app"   # w tym wariancie niewykorzystywana (zarezerwowana)
export SUBNET_DB="snet-db"

# Krótki, unikalny dodatek do nazw globalnie unikalnych (3-6 znaków: małe litery i cyfry)
export SUFFIX="abc123"
export ACR_NAME="acrmodelmanager${SUFFIX}"
export STORAGE_ACCOUNT="stmodelmgr${SUFFIX}"

# Serwer PostgreSQL tworzony przez 00-network-database.sh (nazwa unikalna w całym Azure)
export PG_SERVER="pg-model-manager-${SUFFIX}"
export PG_ADMIN_USER="pgadmin"
export PG_DB="modelmanager"

# Repozytorium GitHub w formacie wlasciciel/repozytorium
export GITHUB_REPO="ERTUK03/model-manager"

# Nazwy zasobów tworzonych przez skrypty (zwykle nie trzeba zmieniać)
# Subskrypcja studencka pozwala na jedno środowisko Container Apps na region, więc obie aplikacje działają w jednym
export ENV_NAME="cae-main"
export BACKEND_APP="ca-backend"
export FRONTEND_APP="ca-frontend"

# Monitoring, logi i alerty (skrypty 05 i 06)
export APPI_NAME="appi-model-manager"
export LOG_DAILY_CAP_GB="1"        # dzienny limit danych w Log Analytics (chroni budżet przed lawiną logów)
export BUDGET_AMOUNT="30"          # miesięczny budżet w walucie rozliczeniowej subskrypcji
export ALERT_EMAILS="adres1@example.com,adres2@example.com"   # adresy zespołu, oddzielone przecinkami
