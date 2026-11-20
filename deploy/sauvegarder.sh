#!/bin/sh
# Sauvegarde de la base PostgreSQL (format compressé de pg_dump).
# Usage : ./sauvegarder.sh          (planifié chaque nuit par cron, voir README)
# Conserve les 14 dernières sauvegardes locales ; copier aussi hors du serveur (voir README).
set -eu
cd "$(dirname "$0")"
set -a; . ./.env; set +a

mkdir -p sauvegardes
fichier="sauvegardes/enso_$(date +%Y-%m-%d_%H%M).dump"

docker compose exec -T db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom > "$fichier"
echo "Sauvegarde créée : $fichier ($(du -h "$fichier" | cut -f1))"

# Rotation : suppression des sauvegardes de plus de 14 jours.
find sauvegardes -name 'enso_*.dump' -mtime +14 -delete
