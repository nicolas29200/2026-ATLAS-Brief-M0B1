# Image de base légère et sécurisée
FROM python:3.11-slim

# Variables d'environnement Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Répertoire de travail
WORKDIR /app

# Installation de uv pour un build ultra-rapide
RUN pip install --no-cache-dir uv


# 5. Optimisation du cache Docker : copier requirements d'abord !
COPY backend/requirements.txt ./backend/
COPY src/ ./src/
COPY pyproject.toml uv.lock ./

# 6. Installation des dépendances via uv dans le Python système
RUN uv pip install --no-cache --system -r backend/requirements.txt

# 7. Copie du reste du code source
COPY README.md ./
COPY backend/ ./backend/
COPY data/ ./data/
COPY models/ ./models/
# Pre-telecharger le lexique VADER au build pour ne plus dependre du reseau au demarrage du conteneur
RUN python -c "import nltk; nltk.download('vader_lexicon',quiet=True)"


# Exposition du port API
EXPOSE 8000


