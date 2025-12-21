# AuctionNet 🎯

Plateforme d'enchères en ligne en temps réel avec Vue.js et Flask.

## 📋 Prérequis

- **Node.js** 20+ et npm
- **Python** 3.11+
- **Docker** (optionnel, pour déploiement)

## 🚀 Installation

### Backend (Flask)

```bash
cd backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur (dev)
python app.py
```

Le backend sera accessible sur `http://localhost:5000`

### Frontend (Vue.js)

```bash
cd frontend

# Installer les dépendances
npm install

# Lancer le serveur de développement
npm run dev
```

Le frontend sera accessible sur `http://localhost:5173`

## 🐳 Docker (Production)

### Avec Docker Compose

```bash
# Lancer tous les services
docker-compose up --build

# En arrière-plan
docker-compose up -d --build
```

### Images individuelles

**Backend:**
```bash
cd backend
docker build -t auctionnet-backend .
docker run -p 5000:5000 auctionnet-backend
```

**Frontend:**
```bash
cd frontend
docker build -t auctionnet-frontend .
docker run -p 80:80 auctionnet-frontend
```

## 📁 Structure du projet

```
AuctionNet-Prod/
├── backend/              # API Flask + WebSocket
│   ├── app.py           # Point d'entrée
│   ├── models/          # Schémas Pydantic
│   ├── services/        # Logique métier
│   └── local_data/      # Base de données YAML
├── frontend/            # Application Vue.js
│   ├── src/
│   │   ├── components/  # Composants réutilisables
│   │   ├── views/       # Pages
│   │   ├── services/    # API & WebSocket
│   │   └── router/      # Configuration routing
│   └── public/          # Assets statiques
└── docker-compose.yml   # Orchestration Docker
```

## 🔑 Variables d'environnement

### Backend (.env)
```env
JWT_SECRET_KEY=votre-secret-key
DB_DIR=./local_data/db
MEDIA_DIR=./local_data/media
```

### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:5000
```

## ✨ Fonctionnalités

- ✅ Authentification JWT
- ✅ Enchères en temps réel (WebSocket)
- ✅ Upload d'images (URL ou fichier local)
- ✅ Gestion de profil utilisateur
- ✅ Filtres et recherche
- ✅ Notifications temps réel

## 🛠️ Commandes utiles

**Frontend:**
```bash
npm run build        # Build production
npm run preview      # Preview du build
npm run lint         # Linter ESLint
```

**Backend:**
```bash
pytest              # Tests unitaires
python -m pip freeze > requirements.txt  # Mise à jour dépendances
```

## 🌐 Déploiement Railway

Le projet est configuré pour Railway avec:
- Nginx pour le frontend (SPA routing)
- WebSocket supporté

## 📝 License

MIT
