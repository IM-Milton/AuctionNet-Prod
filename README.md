# App title : AuctionNet

Plateforme d'enchères en ligne en temps réel avec Vue.js et Flask.

## Fonctionnalités

- Authentification JWT
- Enchères en temps réel (WebSocket)
- Upload d'images (URL ou fichier local)
- Gestion de profil utilisateur
- Filtres et recherche
- Notifications temps réel

## Prérequis

- **Node.js** 20+ et npm
- **Python** 3.11+
     ou
- **Docker**

## Installation

## 1. Via docker

AuctionNet-Prod/
docker compose build (Pour construire les images)
docker compose up -d (Pour lancer les containers)
Accessible sur : http://localhost:5173/

## 2. Sans Docker
### Backend (Flask)

```bash
cd backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur (dev)
python app.py
python3 app.py #(sur Mac)
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


## Structure du projet

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

## Variables d'environnement

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

## Commandes utiles

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

## Déploiement en ligne: 

On utilise Railway pour le déploiment qui permet d'heberger notre site web pour 1 mois gratuitement.

Configuration de Railway : 
- Connexion à notre branch main
- Création de deux services (1 par container)
- Railway détecte et lance le dockerfile

## License

MIT
