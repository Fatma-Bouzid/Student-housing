Student Housing App 🏠

Une application pour aider les étudiants à trouver le meilleur logement étudiant en France et estimer le prix au m².

💡 Fonctionnalités principales
Scraping des annonces : récupère automatiquement les logements depuis ImmoJeune et Studapart.
Nettoyage et traitement des données : supprime les annonces incorrectes et calcule le prix au m².
Analyse et prédiction :
Affiche les tendances (prix moyen, surface moyenne…)
Estime le prix au m² d’un logement grâce à un modèle Random Forest.
Interface utilisateur :
Formulaire interactif pour filtrer par ville, type de logement, surface et budget.
Affichage des résultats en cartes et graphiques avec Streamlit.
Backend API : FastAPI pour récupérer les logements et faire les prédictions.
Conteneurisation : Docker pour lancer le backend et le frontend facilement.

🛠️ Installation et utilisation
Cloner le repo
git clone <URL_DE_TON_REPO>
cd Student_housing_app

Installer les dépendances
pip install -r requirements.txt

Lancer l’application
Avec le script bash run.sh :
./run.sh

Ou manuellement :
Backend :
uvicorn backend.main:app --host 0.0.0.0 --port 8000
Frontend :
streamlit run frontend/app.py
Accéder à l’application
Frontend Streamlit : http://localhost:8501
Backend API : http://localhost:8000

📂 Structure du projet
backend/          # Backend FastAPI + modèle ML + Dockerfile
frontend/         # Interface Streamlit + Dockerfile
data/             # Base SQLite avec les logements
scraper/          # Scripts pour récupérer les annonces
requirements.txt  # Dépendances Python
Dockerfile        # Pour Docker (backend et frontend)
run.sh            # Script pour lancer l’application

⚙️ Technologie utilisées
Python (pandas, numpy, scikit-learn, joblib…)
FastAPI pour le backend
Streamlit pour le frontend
Selenium pour le scraping
SQLite pour la base de données
Docker pour simplifier l’installation
