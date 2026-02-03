# frontend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copier requirements
COPY requirements.txt .

# Installer uniquement Streamlit + pandas + requests
RUN pip install --no-cache-dir streamlit pandas requests

# Copier le code frontend et backend (pour API_URL)
COPY . .

# Exposer le port Streamlit
EXPOSE 8501

# Lancer Streamlit
CMD ["streamlit", "run", "frontend/app.py", "--server.headless=true", "--server.port=8501"]
