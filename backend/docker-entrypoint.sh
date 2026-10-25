#!/bin/sh
# Start kontenera: migracje bazy, opcjonalnie konto administratora, potem serwer.
# Migracje uruchamiamy tutaj, bo baza w Azure leży w prywatnej podsieci
# i nie da się jej zmigrować z komputera dewelopera.
set -e

echo "Migracje bazy danych..."
alembic upgrade head

if [ -n "$ADMIN_EMAIL" ] && [ -n "$ADMIN_PASSWORD" ]; then
  echo "Konto administratora..."
  python -m scripts.create_admin
fi

echo "Start serwera"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --proxy-headers --forwarded-allow-ips "*"
