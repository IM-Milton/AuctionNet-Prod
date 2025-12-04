# Instructions de démarrage

## Backend

1. Installer les dépendances Python :
```bash
cd backend
pip install -r requirements.txt
```

2. Démarrer le serveur Flask :
```bash
python app.py
```

Le backend sera accessible sur `http://localhost:5000`

## Frontend

1. Installer les dépendances Node :
```bash
cd frontend
npm install
```

2. Démarrer le serveur de développement Vite :
```bash
npm run dev
```

Le frontend sera accessible sur `http://localhost:5173`

## Configuration

Le fichier `.env` dans le dossier `frontend` contient l'URL du backend :
```
VITE_API_URL=http://localhost:5000/api
```

## Fonctionnalités

- **Authentification** : Login/Register connecté au backend avec JWT
- **Enchères** : Création et gestion d'enchères
- **Profil utilisateur** : Voir ses enchères et son solde
- **Solde initial** : 100 000 € pour chaque nouvel utilisateur
