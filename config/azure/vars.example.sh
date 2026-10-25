# shellcheck shell=bash
# Skopiuj ten plik jako vars.sh (jest w .gitignore) i uzupełnij wartości.
# Skrypty uruchamiaj w Azure Cloud Shell (Bash) albo lokalnie po `az login`.

# Grupa zasobów i sieć utworzone wcześniej (region jest odczytywany z grupy zasobów)
export RG="rg-model-manager"
export VNET="vnet-model-manager"
export SUBNET_WEB="snet-web"
export SUBNET_APP="snet-app"

# Krótki, unikalny dodatek do nazw globalnie unikalnych (3-6 znaków: małe litery i cyfry)
export SUFFIX="abc123"
export ACR_NAME="acrmodelmanager${SUFFIX}"
export STORAGE_ACCOUNT="stmodelmgr${SUFFIX}"

# Serwer PostgreSQL utworzony wcześniej (adres z portalu: Overview -> Server name) i nazwa bazy aplikacji
export PG_SERVER_FQDN="NAZWA-SERWERA.postgres.database.azure.com"
export PG_DB="modelmanager"

# Repozytorium GitHub w formacie wlasciciel/repozytorium
export GITHUB_REPO="ERTUK03/model-manager"

# Nazwy zasobów tworzonych przez skrypty (zwykle nie trzeba zmieniać)
export ENV_APP="cae-app"
export ENV_WEB="cae-web"
export BACKEND_APP="ca-backend"
export FRONTEND_APP="ca-frontend"
