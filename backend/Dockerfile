# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copier requirements
COPY requirements.txt .

# Installer toutes les dépendances listées dans requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code backend et les données
COPY backend ./backend
COPY data ./data

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]