# --- Etap 1: budowanie aplikacji ---
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Zmienne Vite są wbudowywane w kod podczas budowania
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL
# Wersja (skrót commita) trafia do interfejsu oraz do pliku /version.json, który sprawdza healthcheck po wdrożeniu
ARG VITE_APP_VERSION=dev
ENV VITE_APP_VERSION=$VITE_APP_VERSION
RUN npm run build \
    && printf '{"version":"%s"}\n' "$VITE_APP_VERSION" > dist/version.json

# --- Etap 2: serwowanie przez nginx ---
FROM nginx:alpine
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
# Wymagana zmienna uruchomieniowa: BACKEND_URL (adres back-endu)
EXPOSE 80
