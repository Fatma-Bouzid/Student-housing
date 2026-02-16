Student Housing App 🏠

Application web pour rechercher des logements étudiants, avec FastAPI (backend) et Streamlit (frontend).

Fonctionnalités

Scraping d’annonces depuis ImmoJeune et Studapart

Recherche par ville, type de logement, surface et budget

Interface Streamlit pour afficher les résultats

Dockerisation

Le projet est entièrement dockerisé pour faciliter le déploiement :

Backend : FastAPI sur le port 8000

Frontend : Streamlit sur le port 8501

Gestion simplifiée avec docker-compose

Lancer l’application
# Construire les images
docker-compose build

# Démarrer backend et frontend
docker-compose up


Accéder au frontend : http://localhost:8501

Remarques

Base de données SQLite située dans data/

Toutes les dépendances installées automatiquement dans les containers