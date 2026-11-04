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
COPY frontend/requirements.txt ./frontend/

# 6. Installation des dépendances via uv dans le Python système
RUN uv pip install --no-cache --system -r frontend/requirements.txt

COPY frontend/ ./frontend/

EXPOSE 8501
