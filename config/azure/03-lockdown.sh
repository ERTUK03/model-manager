#!/usr/bin/env bash
# Krok 3 (na końcu, gdy aplikacja już działa): utwardzenie zabezpieczeń sieciowych i blokada przypadkowego usunięcia.
# Bezpieczne do ponownego uruchomienia. Po zakończeniu uruchom ./04-verify-security.sh.
set -euo pipefail
cd "$(dirname "$0")"
# shellcheck source=/dev/null
source ./vars.sh

echo "1/4 Porty zarządcze (SSH 22, RDP 3389) zablokowane z Internetu w każdej warstwie"
for nsg in nsg-web nsg-app nsg-db; do
  az network nsg rule create --resource-group "$RG" --nsg-name "$nsg" --name deny-mgmt-ports-internet \
    --priority 110 --direction Inbound --access Deny --protocol '*' \
    --source-address-prefixes Internet --source-port-ranges '*' \
    --destination-address-prefixes '*' --destination-port-ranges 22 3389 --output none
done

echo "2/4 Baza: blokada całego pozostałego ruchu przychodzącego (poza regułą allow-postgres-from-web)"
az network nsg rule create --resource-group "$RG" --nsg-name nsg-db --name deny-all-inbound \
  --priority 4000 --direction Inbound --access Deny --protocol '*' \
  --source-address-prefixes VirtualNetwork Internet --source-port-ranges '*' \
  --destination-address-prefixes '*' --destination-port-ranges '*' --output none

echo "3/4 Front-end: wymuszenie HTTPS (żądania HTTP są przekierowywane na HTTPS)"
if ! az containerapp ingress update --name "$FRONTEND_APP" --resource-group "$RG" --allow-insecure false --output none; then
  echo "UWAGA: nie udało się ustawić tego poleceniem. Ustaw ręcznie: portal -> $FRONTEND_APP -> Ingress -> odznacz \"Allow insecure connections\"."
fi

echo "4/4 Blokada usunięcia grupy zasobów (ochrona przed przypadkowym skasowaniem)"
az lock create --name nie-usuwac --lock-type CanNotDelete --resource-group "$RG" --output none

echo "Gotowe. Zdejmowanie blokady po zakończeniu projektu: az lock delete --name nie-usuwac --resource-group $RG"
echo "Sprawdź teraz, że aplikacja nadal działa pod publicznym adresem, a potem uruchom ./04-verify-security.sh"
