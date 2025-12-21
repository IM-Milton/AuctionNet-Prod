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

# Copie de la configuration Nginx pour gérer le routing SPA
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
