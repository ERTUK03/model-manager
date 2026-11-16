#!/usr/bin/env bash
# Krok 6: alert budżetowy z powiadomieniami e-mail dla zespołu (Cost Management).
# Progi: 50%, 80% i 100% wydatków oraz 100% prognozy. Bezpieczne do ponownego uruchomienia (aktualizuje budżet).
set -euo pipefail
cd "$(dirname "$0")"
# shellcheck source=/dev/null
source ./vars.sh
BUDGET_AMOUNT="${BUDGET_AMOUNT:-30}"
BUDGET_NAME="${BUDGET_NAME:-budzet-model-manager}"
ALERT_EMAILS="${ALERT_EMAILS:?Ustaw ALERT_EMAILS w vars.sh (adresy oddzielone przecinkami)}"

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
START=$(date -u +%Y-%m-01T00:00:00Z)
END=$(date -u -d "+2 years" +%Y-%m-01T00:00:00Z)
URL="https://management.azure.com/subscriptions/${SUBSCRIPTION_ID}/providers/Microsoft.Consumption/budgets/${BUDGET_NAME}?api-version=2023-05-01"

build_body() { # kwota, początek, koniec, adresy, czy dodać prognozę (true/false)
  python3 - "$@" <<'PY'
import json
import sys

amount, start, end, emails, forecast = sys.argv[1:6]
contacts = [e.strip() for e in emails.split(",") if e.strip()]


def rule(threshold, kind):
    return {"enabled": True, "operator": "GreaterThan", "threshold": threshold, "thresholdType": kind, "contactEmails": contacts}


notifications = {"Actual50": rule(50, "Actual"), "Actual80": rule(80, "Actual"), "Actual100": rule(100, "Actual")}
if forecast == "true":
    notifications["Forecast100"] = rule(100, "Forecasted")
body = {
    "properties": {
        "category": "Cost",
        "amount": float(amount),
        "timeGrain": "Monthly",
        "timePeriod": {"startDate": start, "endDate": end},
        "notifications": notifications,
    }
}
print(json.dumps(body))
PY
}

echo "Budżet $BUDGET_NAME: ${BUDGET_AMOUNT} miesięcznie, powiadomienia: ${ALERT_EMAILS}"
if ! az rest --method put --url "$URL" --body "$(build_body "$BUDGET_AMOUNT" "$START" "$END" "$ALERT_EMAILS" true)" --output none; then
  echo "Nie udało się utworzyć budżetu z alertem prognozy. Próbuję bez progu prognozy..."
  az rest --method put --url "$URL" --body "$(build_body "$BUDGET_AMOUNT" "$START" "$END" "$ALERT_EMAILS" false)" --output none
fi
echo "Gotowe. Budżet widać w portalu: Cost Management -> Budgets."
echo "Dane o kosztach mają opóźnienie do kilku godzin, więc pierwsze powiadomienie może przyjść z opóźnieniem."
