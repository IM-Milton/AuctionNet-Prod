# frontend/Dockerfile

# Étape 1 : build Vue
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Étape 2 : servir les fichiers avec Nginx
FROM nginx:1.27-alpine

# Copie du build dans le dossier servit par Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Optionnel : config nginx custom si tu veux un proxy /api
# Copier un fichier nginx.conf si nécessaire.

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
