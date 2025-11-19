# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture du projet

Ce projet implémente un système de monitoring ML pour un modèle de prédiction de survie sur le Titanic avec une stack de monitoring complète utilisant Docker.

### Stack technique

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Grafana   │◄───┤ Prometheus  │◄───┤  FastAPI    │
│   (3000)    │    │   (9090)    │    │   (8000)    │
└─────────────┘    └─────────────┘    └─────────────┘
                           ▲
                           │
                    ┌──────┴──────┐
                    │  cAdvisor   │
                    │   (8080)    │
                    └─────────────┘
```

### Composants principaux

- **api/** : Application FastAPI avec instrumentation Prometheus
- **prometheus/** : Configuration de scraping (intervalle 15s) pour api:8000, prometheus:9090 et cadvisor:8080
- **grafana/** : Dashboards et datasources provisionnés automatiquement
- **notebooks/** : Exploration des données (01_data_exploration.ipynb) et entraînement du modèle (02_model_training.ipynb)
- **models/** : Artéfacts ML sauvegardés
- **reports/** : Rapports de performance et métriques générés
- **data/** : Datasets Titanic (raw et nettoyé)

### Réseau Docker

Tous les services communiquent via le réseau bridge `ml-monitoring`. Les volumes persistants sont `prometheus_data` et `grafana_data`.

## Commandes de développement

### Docker (environnement principal)

```bash
# Démarrer l'ensemble de la stack
docker-compose up -d

# Vérifier l'état des services
docker-compose ps

# Voir les logs en temps réel
docker-compose logs -f
docker-compose logs -f api         # Logs de l'API seulement
docker-compose logs -f prometheus  # Logs de Prometheus seulement

# Arrêter les services
docker-compose down

# Rebuild complet après modifications du code
docker-compose up -d --build

# Nettoyer volumes et données (ATTENTION: supprime les données)
docker-compose down -v
```

### Développement local (sans Docker)

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'API en mode développement avec hot-reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Tests

```bash
# Exécuter les tests
pytest tests/

# Tests avec coverage
pytest tests/ --cov=api

# Tests asynchrones (utilise pytest-asyncio et httpx)
pytest tests/ -v
```

### Points d'accès

- **API Docs**: http://localhost:8000/docs (OpenAPI interactive)
- **Métriques API**: http://localhost:8000/metrics
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **cAdvisor**: http://localhost:8080

## Principes de développement

### Structure du code FastAPI

L'API est construite dans `api/main.py` avec instrumentation Prometheus automatique via `prometheus-fastapi-instrumentator`. Le module `api/metrics/monitoring.py` contient les imports Evidently pour le monitoring ML (ClassificationPerformanceMetric).

### Monitoring personnalisé

Pour ajouter des métriques personnalisées:
1. Définir les métriques Prometheus dans `api/metrics/monitoring.py`
2. Les exposer via l'endpoint `/metrics` (déjà configuré)
3. Prometheus scrappe automatiquement toutes les 15s

### Monitoring ML avec Evidently

Evidently est installé pour détecter le drift de données et monitorer les performances du modèle. Le module `api/metrics/monitoring.py` importe déjà `Report` et `ClassificationPerformanceMetric`.

### Healthcheck

L'API doit exposer un endpoint `/health` pour le healthcheck Docker (configuré dans docker-compose.yml avec retry 3 fois toutes les 30s).

## Configuration

### Variables d'environnement

- `ENVIRONMENT=production` (défini dans docker-compose.yml pour l'API)

### Grafana

- Identifiants par défaut: admin/admin
- Les datasources sont provisionnées depuis `grafana/datasources/datasources.yml`
- Les dashboards sont chargés depuis `grafana/dashboards/`

### Prometheus

Configuration dans `prometheus/prometheus.yml`:
- Intervalle de scraping global: 15s
- Jobs configurés: prometheus, api, cadvisor

## Dataset et modèle

- Dataset brut: `data/raw/Titanic-Dataset.csv`
- Dataset nettoyé: `data/titanic_cleaned_dataset.csv`
- Notebooks d'analyse: `notebooks/01_data_exploration.ipynb` et `notebooks/02_model_training.ipynb`
- Modèles sauvegardés dans: `models/`

## Dépendances critiques

- FastAPI + Uvicorn (ASGI server)
- prometheus-client + prometheus-fastapi-instrumentator
- Evidently (monitoring ML et drift detection)
- scikit-learn, pandas, numpy (ML stack)
- pytest, pytest-asyncio, httpx (tests)
- loguru (logging structuré)

## Branche principale

La branche par défaut pour les PRs est `dev` (pas `main`).