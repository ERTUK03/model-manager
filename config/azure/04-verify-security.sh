#!/usr/bin/env bash
# Krok 4: automatyczna weryfikacja zabezpieczeń wdrożonej aplikacji. Wynik (PASS/FAIL) jest dowodem do dokumentacji.
# Sprawdza reguły zapory (z uwzględnieniem priorytetów), izolację bazy, ingress aplikacji, HTTPS i certyfikat,
# przekierowanie HTTP -> HTTPS, nagłówki bezpieczeństwa oraz ustawienia magazynu plików.
set -uo pipefail
cd "$(dirname "$0")" || exit 1
# shellcheck source=/dev/null
source ./vars.sh

failures=0
check() { # opis, polecenie do wykonania (sukces polecenia = sprawdzenie udane)
  local description="$1"
  shift
  if "$@"; then
    echo "PASS  $description"
  else
    echo "FAIL  $description"
    failures=$((failures + 1))
  fi
}
lower() { tr '[:upper:]' '[:lower:]'; }
# shellcheck disable=SC2329  # wywoływana pośrednio przez check
is_https_redirect() { # odpowiedź w formacie "kod adres"
  case "$1" in
    "301 https://"* | "302 https://"* | "307 https://"* | "308 https://"*) return 0 ;;
    *) return 1 ;;
  esac
}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

echo "== 1. Reguły zapory (NSG)"
subnet_cidr() { az network vnet subnet show --resource-group "$RG" --vnet-name "$VNET" --name "$1" --query addressPrefix -o tsv; }
for nsg in nsg-web nsg-app nsg-db; do
  az network nsg rule list --resource-group "$RG" --nsg-name "$nsg" --output json > "$tmp/$nsg.json"
done
python3 audit_nsg.py --web-cidr "$(subnet_cidr "$SUBNET_WEB")" --app-cidr "$(subnet_cidr "$SUBNET_APP")" \
  --db-cidr "$(subnet_cidr "$SUBNET_DB")" "$tmp/nsg-web.json" "$tmp/nsg-app.json" "$tmp/nsg-db.json" \
  || failures=$((failures + $?))

echo "== 2. Baza danych: izolacja od Internetu"
public=$(az postgres flexible-server show --resource-group "$RG" --name "$PG_SERVER" --query network.publicNetworkAccess -o tsv 2>/dev/null)
delegated=$(az postgres flexible-server show --resource-group "$RG" --name "$PG_SERVER" --query network.delegatedSubnetResourceId -o tsv 2>/dev/null)
check "Serwer PostgreSQL nie ma publicznego punktu końcowego (publicNetworkAccess=${public:-brak})" [ "$public" = "Disabled" ]
check "Serwer działa w prywatnej podsieci (dostęp prywatny w sieci wirtualnej)" [ -n "$delegated" ]

echo "== 3. Ingress aplikacji"
ingress() { az containerapp show --name "$1" --resource-group "$RG" --query "properties.configuration.ingress.$2" -o tsv 2>/dev/null | lower; }
fe_external=$(ingress "$FRONTEND_APP" external)
fe_insecure=$(ingress "$FRONTEND_APP" allowInsecure)
fe_fqdn=$(az containerapp show --name "$FRONTEND_APP" --resource-group "$RG" --query properties.configuration.ingress.fqdn -o tsv 2>/dev/null)
be_external=$(ingress "$BACKEND_APP" external)
be_fqdn=$(az containerapp show --name "$BACKEND_APP" --resource-group "$RG" --query properties.configuration.ingress.fqdn -o tsv 2>/dev/null)
check "Front-end ma ingress zewnętrzny (jedyny publiczny punkt wejścia)" [ "$fe_external" = "true" ]
check "Front-end nie dopuszcza ruchu niezaszyfrowanego (allowInsecure=${fe_insecure:-brak})" [ "$fe_insecure" != "true" ]
check "Back-end ma ingress wewnętrzny (brak publicznego adresu, external=${be_external:-brak})" [ "$be_external" = "false" ]

if [ -z "$fe_fqdn" ]; then
  echo "FAIL  Nie udało się odczytać adresu front-endu, pomijam testy sieciowe"
  failures=$((failures + 1))
else
  echo "== 4. HTTPS i certyfikat (https://$fe_fqdn)"
  https=$(curl -sS -o /dev/null -w '%{http_code} %{ssl_verify_result}' --max-time 20 "https://$fe_fqdn/" 2>/dev/null || true)
  check "HTTPS odpowiada kodem 200, a certyfikat przechodzi weryfikację łańcucha zaufania (wynik: $https)" [ "$https" = "200 0" ]
  tls=$(echo | openssl s_client -connect "$fe_fqdn:443" -servername "$fe_fqdn" 2>/dev/null)
  protocol=$(echo "$tls" | grep -oE 'TLSv1\.[23]' | head -1)
  check "Połączenie używa nowoczesnego protokołu (${protocol:-nie ustalono})" [ -n "$protocol" ]
  echo "$tls" | openssl x509 -noout -issuer -subject -dates 2>/dev/null | sed 's/^/        /'

  echo "== 5. Przekierowanie HTTP -> HTTPS"
  redirect=$(curl -sS -o /dev/null -w '%{http_code} %{redirect_url}' --max-time 20 "http://$fe_fqdn/" 2>/dev/null || true)
  check "Żądanie HTTP jest przekierowywane na HTTPS (odpowiedź: $redirect)" is_https_redirect "$redirect"

  echo "== 6. Nagłówki bezpieczeństwa"
  headers=$(curl -sSI --max-time 20 "https://$fe_fqdn/" 2>/dev/null | tr -d '\r')
  check "Odpowiedź zawiera nagłówek HSTS (Strict-Transport-Security)" grep -qi '^strict-transport-security:' <<< "$headers"
  check "Odpowiedź zawiera X-Content-Type-Options: nosniff" grep -qi '^x-content-type-options: nosniff' <<< "$headers"

  echo "== 7. Dostępność API"
  via_front=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 20 "https://$fe_fqdn/api/health/ready" 2>/dev/null || true)
  check "API działa przez front-end (/api/health/ready: $via_front)" [ "$via_front" = "200" ]
  if [ -n "$be_fqdn" ]; then
    direct=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 10 "https://$be_fqdn/api/health" 2>/dev/null || true)
    check "Back-end nie jest dostępny bezpośrednio z Internetu ($be_fqdn: kod ${direct:-brak})" [ "$direct" != "200" ]
  fi
fi

echo "== 8. Magazyn plików (Blob Storage)"
storage() { az storage account show --resource-group "$RG" --name "$STORAGE_ACCOUNT" --query "$1" -o tsv 2>/dev/null | lower; }
check "Anonimowy dostęp do obiektów jest wyłączony" [ "$(storage allowBlobPublicAccess)" = "false" ]
check "Minimalna wersja TLS to 1.2" [ "$(storage minimumTlsVersion)" = "tls1_2" ]
check "Dozwolony jest wyłącznie ruch HTTPS" [ "$(storage enableHttpsTrafficOnly)" = "true" ]

echo
if [ "$failures" -eq 0 ]; then
  echo "WYNIK: wszystkie sprawdzenia udane"
else
  echo "WYNIK: nieudane sprawdzenia: $failures"
fi
exit $((failures > 255 ? 255 : failures))
