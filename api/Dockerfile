FROM python:3.10-slim

# Crée un dossier /app dans le conteneur
WORKDIR /app

# On copie le fichier requirements.txt (qui est à la racine du projet)
COPY requirements.txt .

# On installe les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# On copie le dossier api/ dans /app/api
COPY api/ ./api

# On se place dans /app/api
WORKDIR /app/api

# (Optionnel) dire à Python où est le projet
ENV PYTHONPATH=/app

# On expose le port 8000
EXPOSE 8000

# Commande pour lancer l'API FastAPI avec uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]