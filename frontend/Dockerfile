# --- Etap 1: budowanie aplikacji ---
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Zmienne Vite są wbudowywane w kod podczas budowania
ARG VITE_API_URL=/api
ARG VITE_USE_MOCK=false
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_USE_MOCK=$VITE_USE_MOCK
RUN npm run build

# --- Etap 2: serwowanie przez nginx ---
FROM nginx:alpine
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
# Wymagana zmienna uruchomieniowa: BACKEND_URL (adres back-endu)
EXPOSE 80
