# backend/Dockerfile
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier requirements
COPY requirements.txt .

# Installer uniquement FastAPI + uvicorn + pandas pour le backend
RUN pip install --no-cache-dir fastapi uvicorn pandas

# Copier le code du backend
COPY backend ./backend
COPY data ./data

# Exposer le port
EXPOSE 8000

# Lancer FastAPI
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
