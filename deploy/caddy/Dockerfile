# Image du point d'entrée : Caddy sert le frontend et relaie /api vers l'API.
# Construite depuis la racine du dépôt : docker build -f deploy/caddy/Dockerfile .

# Étape 1 : construire le frontend (fichiers statiques HTML/CSS/JS).
FROM node:24-alpine AS construction
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Étape 2 : image finale légère, sans Node ni code source, seulement les fichiers construits.
FROM caddy:2-alpine
COPY deploy/caddy/Caddyfile /etc/caddy/Caddyfile
COPY --from=construction /frontend/dist /srv
