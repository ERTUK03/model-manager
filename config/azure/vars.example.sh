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
