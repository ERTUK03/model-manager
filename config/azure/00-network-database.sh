#!/usr/bin/env bash
# Krok 0: grupa zasobów, sieć wirtualna z trzema podsieciami, grupy zabezpieczeń (NSG) i baza PostgreSQL
# w trybie prywatnym. Pozwala odtworzyć całą podstawę infrastruktury jednym poleceniem.
set -euo pipefail
cd "$(dirname "$0")"
# shellcheck source=/dev/null
source ./vars.sh

echo "1/6 Grupa zasobów ($RG, region $LOCATION)"
az group create --name "$RG" --location "$LOCATION" --output none

echo "2/6 Rejestracja dostawców zasobów"
for namespace in Microsoft.Network Microsoft.DBforPostgreSQL; do
  az provider register --namespace "$namespace" --wait
done

echo "3/6 Grupy zabezpieczeń sieci (NSG) i reguły dostępu"
for nsg in nsg-web nsg-app nsg-db; do
  az network nsg create --resource-group "$RG" --name "$nsg" --location "$LOCATION" --output none
done
# Front-end: Internet może łączyć się na portach 80 i 443
az network nsg rule create --resource-group "$RG" --nsg-name nsg-web --name allow-http-https-internet \
  --priority 100 --direction Inbound --access Allow --protocol Tcp \
  --source-address-prefixes Internet --source-port-ranges '*' \
  --destination-address-prefixes '*' --destination-port-ranges 80 443 --output none
# Baza: tylko podsieć z aplikacjami (snet-web) i tylko port PostgreSQL
az network nsg rule create --resource-group "$RG" --nsg-name nsg-db --name allow-postgres-from-web \
  --priority 100 --direction Inbound --access Allow --protocol Tcp \
  --source-address-prefixes 10.0.0.0/23 --source-port-ranges '*' \
  --destination-address-prefixes '*' --destination-port-ranges 5432 --output none

echo "4/6 Sieć wirtualna 10.0.0.0/16 i trzy podsieci"
az network vnet create --resource-group "$RG" --name "$VNET" --location "$LOCATION" \
  --address-prefixes 10.0.0.0/16 --output none
az network vnet subnet create --resource-group "$RG" --vnet-name "$VNET" --name "$SUBNET_WEB" \
  --address-prefixes 10.0.0.0/23 --network-security-group nsg-web --delegations Microsoft.App/environments --output none
az network vnet subnet create --resource-group "$RG" --vnet-name "$VNET" --name "$SUBNET_APP" \
  --address-prefixes 10.0.2.0/23 --network-security-group nsg-app --output none
az network vnet subnet create --resource-group "$RG" --vnet-name "$VNET" --name "$SUBNET_DB" \
  --address-prefixes 10.0.4.0/24 --network-security-group nsg-db \
  --delegations Microsoft.DBforPostgreSQL/flexibleServers --output none

echo "5/6 Serwer PostgreSQL (dostęp prywatny, najmniejszy wariant Burstable, bez wysokiej dostępności)"
read -rsp "Hasło administratora PostgreSQL (min. 8 znaków, litery i cyfry; zapisz je w menedżerze haseł): " PG_PASSWORD
echo

# 1. Tworzenie stacji/strefy prywatnego DNS wymaganej dla Flexible Server z integracją VNet
DNS_ZONE="private.postgres.database.azure.com"

az network private-dns zone create \
  --resource-group "$RG" \
  --name "$DNS_ZONE" \
  --output none || true

# 2. Powiązanie strefy DNS z siecią wirtualną (jeśli jeszcze nie powiązana)
VNET_ID=$(az network vnet show --resource-group "$RG" --name "$VNET" --query id -o tsv)
az network private-dns link vnet create \
  --resource-group "$RG" \
  --zone-name "$DNS_ZONE" \
  --name "${VNET}-dns-link" \
  --virtual-network "$VNET_ID" \
  --registration-enabled false \
  --output none || true

# 3. Tworzenie serwera PostgreSQL z poprawną strefą DNS
az postgres flexible-server create --resource-group "$RG" --name "$PG_SERVER" --location "$LOCATION" \
  --admin-user "$PG_ADMIN_USER" --admin-password "$PG_PASSWORD" \
  --tier Burstable --sku-name Standard_B1ms --storage-size 32 --version 16 \
  --vnet "$VNET" --subnet "$SUBNET_DB" \
  --private-dns-zone "$DNS_ZONE" \
  --zonal-resiliency Disabled --backup-retention 7 --yes

echo "6/6 Gotowe."
echo "  Serwer PostgreSQL: $(az postgres flexible-server show --resource-group "$RG" --name "$PG_SERVER" --query fullyQualifiedDomainName -o tsv)"
echo "  Baza: $PG_DB, administrator: $PG_ADMIN_USER"
echo "  Następny krok: ./01-provision.sh"
