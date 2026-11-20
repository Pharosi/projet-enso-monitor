#!/bin/sh
# Restauration d'une sauvegarde : remplace le contenu actuel de la base.
# Usage : ./restaurer.sh sauvegardes/enso_2026-11-21_0300.dump
set -eu
cd "$(dirname "$0")"
set -a; . ./.env; set +a

if [ $# -ne 1 ] || [ ! -f "$1" ]; then
  echo "Usage : $0 <fichier .dump>" >&2
  exit 1
fi

echo "Restauration de $1 dans la base « $POSTGRES_DB »…"
docker compose stop api
docker compose exec -T db pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists < "$1"
docker compose start api
echo "Restauration terminée."
