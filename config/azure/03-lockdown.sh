#!/usr/bin/env bash
# Krok 3 (na końcu, gdy aplikacja już działa): zamknięcie dostępu do bazy i blokada przypadkowego usunięcia.
set -euo pipefail
cd "$(dirname "$0")"
# shellcheck source=/dev/null
source ./vars.sh

echo "1/2 Baza: blokada całego pozostałego ruchu przychodzącego (poza regułą allow-postgres-from-web)"
az network nsg rule create --resource-group "$RG" --nsg-name nsg-db --name deny-all-inbound \
  --priority 4000 --direction Inbound --access Deny --protocol '*' \
  --source-address-prefixes VirtualNetwork Internet --source-port-ranges '*' \
  --destination-address-prefixes '*' --destination-port-ranges '*' --output none

echo "2/2 Blokada usunięcia grupy zasobów (ochrona przed przypadkowym skasowaniem)"
az lock create --name nie-usuwac --lock-type CanNotDelete --resource-group "$RG" --output none
echo "Gotowe. Po zakończeniu projektu zdejmij blokadę: az lock delete --name nie-usuwac --resource-group $RG"
echo "Sprawdź teraz, że aplikacja nadal działa pod publicznym adresem."
