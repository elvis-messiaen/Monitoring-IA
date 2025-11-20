# Monitoring-IA

Système complet de monitoring pour un modèle de Machine Learning de prédiction de survie sur le Titanic.

## Table des matières

- [Introduction](#introduction)
- [Architecture du projet](#architecture-du-projet)
- [Prérequis](#prérequis)
- [Installation et démarrage](#installation-et-démarrage)
- [Accès aux interfaces](#accès-aux-interfaces)
- [Guide d'utilisation](#guide-dutilisation)
- [Structure du projet](#structure-du-projet)
- [Configuration](#configuration)
- [Développement local](#développement-local)
- [Dépannage](#dépannage)

---

## Introduction

Ce projet implémente une stack complète de monitoring pour un modèle de Machine Learning qui prédit la survie des passagers du Titanic. Il combine:

- **API FastAPI** : API REST pour effectuer des prédictions
- **Prometheus** : Collecte et stockage des métriques
- **Grafana** : Visualisation des métriques avec dashboards interactifs
- **cAdvisor** : Monitoring des ressources des conteneurs Docker
- **Evidently AI** : Détection de drift et analyse de performance du modèle

L'ensemble de la stack est orchestrée avec Docker Compose pour un déploiement simple et reproductible.

---

## Architecture du projet

```
┌─────────────────────────────────────────────────────────────┐
│                     STACK DE MONITORING                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Grafana   │◄────────┤ Prometheus  │◄────────┤  FastAPI    │
│             │         │             │         │             │
│ Dashboards  │         │  Collecte   │         │  Modèle ML  │
│  Graphiques │         │  Métriques  │         │ Prédictions │
│             │         │             │         │             │
│  Port 3000  │         │  Port 9090  │         │  Port 8000  │
└─────────────┘         └─────────────┘         └─────────────┘
                               ▲
                               │
                               │ Scrape toutes les 15s
                               │
                        ┌──────┴────────┐
                        │   cAdvisor    │
                        │               │
                        │  Monitoring   │
                        │  Conteneurs   │
                        │               │
                        │   Port 8080   │
                        └───────────────┘
```

### Composants principaux

| Composant | Rôle | Port |
|-----------|------|------|
| **FastAPI** | API REST avec endpoints de prédiction et métriques personnalisées | 8000 |
| **Prometheus** | Collecte des métriques toutes les 15 secondes depuis l'API et cAdvisor | 9090 |
| **Grafana** | Interface de visualisation avec 2 dashboards pré-configurés | 3000 |
| **cAdvisor** | Monitoring des ressources CPU/RAM/Network des conteneurs | 8080 |

---

## Prérequis

Avant de commencer, assurez-vous d'avoir installé:

- **Docker** (version 20.10 ou supérieure)
- **Docker Compose** (version 2.0 ou supérieure)
- **Git**
- **Python 3.11+** (uniquement pour le développement local sans Docker)

### Vérifier les installations

```bash
# Vérifier Docker
docker --version

# Vérifier Docker Compose
docker-compose --version

# Vérifier Git
git --version
```

---

## Installation et démarrage

### Étape 1 : Cloner le projet

```bash
git clone https://github.com/elvis-messiaen/Monitoring-IA.git
cd Monitoring-IA
```

### Étape 2 : Démarrer tous les services

```bash
# Construire et démarrer tous les conteneurs en arrière-plan
docker-compose up -d --build
```

Cette commande va:
1. Construire l'image Docker de l'API FastAPI
2. Télécharger les images Prometheus, Grafana et cAdvisor
3. Démarrer les 4 services
4. Créer le réseau `ml-monitoring` pour la communication entre conteneurs

### Étape 3 : Vérifier que tout fonctionne

```bash
# Voir l'état des conteneurs
docker-compose ps

# Devrait afficher 4 conteneurs en état "Up"
# - titanic-ml-api
# - prometheus
# - grafana
# - cadvisor
```

### Étape 4 : Tester l'API

```bash
# Vérifier la santé de l'API
curl http://localhost:8000/health

# Devrait retourner: {"status":"healthy","timestamp":...}
```

---

## Accès aux interfaces

Une fois tous les services démarrés, vous pouvez accéder aux différentes interfaces:

| Interface | URL | Identifiants | Description |
|-----------|-----|--------------|-------------|
| **API Documentation** | http://localhost:8000/docs | - | Documentation Swagger interactive |
| **API Health** | http://localhost:8000/health | - | Endpoint de santé |
| **Métriques Prometheus** | http://localhost:8000/metrics | - | Métriques brutes au format Prometheus |
| **Grafana** | http://localhost:3000 | admin / admin | Dashboards de visualisation |
| **Prometheus** | http://localhost:9090 | - | Interface de requêtes Prometheus |
| **cAdvisor** | http://localhost:8080 | - | Monitoring des conteneurs |

### Premiers pas avec Grafana

1. Ouvrir http://localhost:3000
2. Se connecter avec `admin` / `admin`
3. (Optionnel) Changer le mot de passe
4. Cliquer sur l'icône "Dashboards" dans le menu de gauche
5. Deux dashboards sont disponibles:
   - **ML Metrics** : Métriques du modèle de Machine Learning
   - **API Performance** : Performances de l'API FastAPI

---

## Guide d'utilisation

### 1. Effectuer des prédictions

#### Prédiction simple (un passager)

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"Sex": "F", "Fare": 30.0}'

# Réponse: {"prediction": "Survived"}
```

#### Prédictions multiples (batch)

```bash
curl -X POST "http://localhost:8000/predict_many" \
  -H "Content-Type: application/json" \
  -d '{
    "passengers": [
      {"Sex": "M", "Fare": 10.0},
      {"Sex": "F", "Fare": 50.0}
    ]
  }'

# Réponse: {"predictions": ["Died", "Survived"]}
```

#### Utiliser le script de simulation

Pour générer rapidement 10 prédictions aléatoires et peupler les métriques:

```bash
# Depuis la racine du projet
python scripts/simuler_predictions.py
```

Ce script va:
- Générer 10 passagers avec des caractéristiques aléatoires
- Effectuer une prédiction pour chacun
- Afficher les statistiques
- Enregistrer les métriques dans Prometheus

### 2. Visualiser les métriques dans Grafana

#### Dashboard "ML Metrics"

Accès: http://localhost:3000/d/ml-metrics

Ce dashboard affiche:
- **Prédictions par classe** : Nombre de prédictions "Survived" vs "Died" au fil du temps
- **Latence de prédiction** : Temps de réponse du modèle (p50, p95, p99)
- **Accuracy du modèle** : Précision actuelle du modèle (jauge 0-1)
- **Score de drift** : Détection de dérive des données (jauge 0-1)
- **Confiance des prédictions** : Niveau de confiance moyen par classe
- **Taux d'erreur** : Erreurs de prédiction par type

#### Dashboard "API Performance"

Accès: http://localhost:3000/d/api-performance

Ce dashboard affiche:
- **Latence des requêtes HTTP** : Temps de réponse des endpoints (p50, p95)
- **Requêtes par seconde** : Trafic de l'API
- **Taux d'erreur HTTP** : Erreurs 4xx et 5xx
- **Ressources des conteneurs** : Utilisation CPU et RAM

#### Conseils pour les dashboards

- Sélectionner l'intervalle de temps "Last 15 minutes" pour voir les données récentes
- Activer le rafraîchissement automatique (bouton en haut à droite, choisir 10s)
- Cliquer sur un graphique pour voir la requête Prometheus sous-jacente

### 3. Requêter Prometheus directement

Accès: http://localhost:9090

#### Requêtes PromQL utiles

```promql
# Nombre total de prédictions par classe
ml_predictions_total

# Taux de prédictions (par seconde)
rate(ml_predictions_total[5m])

# Latence moyenne de prédiction
rate(ml_prediction_latency_seconds_sum[5m]) / rate(ml_prediction_latency_seconds_count[5m])

# Accuracy actuelle du modèle
ml_model_accuracy

# Score de drift des données
ml_data_drift_score

# Confiance moyenne par classe
ml_prediction_confidence

# Taux de requêtes HTTP
rate(http_requests_total[5m])

# Latence HTTP au 95e percentile
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### 4. Générer des rapports Evidently

Evidently génère des rapports HTML interactifs pour analyser le drift et les performances du modèle.

#### Prérequis : Environnement virtuel Python 3.10

**IMPORTANT** : Pour générer les rapports Evidently, vous devez utiliser Python 3.10 dans un environnement virtuel.

```bash
# Créer un environnement virtuel avec Python 3.10
python3.10 -m venv .venv

# Activer l'environnement virtuel
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

#### Générer un rapport de drift

```bash
# S'assurer que l'environnement virtuel est activé
source .venv/bin/activate

# Rapport avec données de test
python scripts/generer_rapport_test.py

# Rapport avec prédictions réelles
python scripts/generer_rapport_avec_predictions.py

# Ouvrir le rapport dans le navigateur
open reports/drift_report_with_predictions_*.html
```

### 5. Consulter les métriques brutes

Accès: http://localhost:8000/metrics

Cet endpoint expose toutes les métriques au format texte Prometheus:

```
# HELP ml_predictions_total Nombre total de prédictions effectuées
# TYPE ml_predictions_total counter
ml_predictions_total{model_version="v1.0",prediction_class="survived"} 26.0
ml_predictions_total{model_version="v1.0",prediction_class="died"} 14.0

# HELP ml_model_accuracy Précision actuelle du modèle
# TYPE ml_model_accuracy gauge
ml_model_accuracy{model_version="v1.0"} 0.7876106194690266
```

### 6. Calculer l'accuracy automatiquement

L'accuracy est calculée automatiquement au démarrage de l'API sur le dataset de test.

Pour la recalculer manuellement:

```bash
curl -X POST "http://localhost:8000/monitoring/calculate-accuracy"
```

### 7. Monitoring des conteneurs avec cAdvisor

Accès: http://localhost:8080

cAdvisor affiche:
- Utilisation CPU par conteneur
- Consommation mémoire (RAM)
- I/O réseau et disque
- Historique des ressources

---

## Structure du projet

```
Monitoring-IA/
├── api/                              # Application FastAPI
│   ├── main.py                       # Point d'entrée avec endpoints
│   ├── models.py                     # Schémas Pydantic (Passenger, Passengers)
│   ├── predict.py                    # Logique de prédiction
│   ├── config.py                     # Configuration de l'application
│   ├── metrics/                      # Module de monitoring
│   │   ├── __init__.py               # Export des fonctions principales
│   │   └── monitoring.py             # Métriques Prometheus + Evidently
│   └── Dockerfile                    # Image Docker de l'API
│
├── grafana/                          # Configuration Grafana
│   ├── datasources/
│   │   └── datasources.yml           # Datasources Prometheus auto-provisionnées
│   └── dashboards/
│       ├── dashboard.yml             # Configuration de provisioning
│       ├── ml-metrics.json           # Dashboard métriques ML
│       └── api-performance.json      # Dashboard performance API
│
├── prometheus/                       # Configuration Prometheus
│   └── prometheus.yml                # Scraping config (API, cAdvisor, Prometheus)
│
├── notebooks/                        # Notebooks Jupyter
│   ├── 01_data_exploration.ipynb     # Exploration du dataset Titanic
│   └── 02_model_training.ipynb       # Entraînement du modèle
│
├── data/                             # Datasets
│   ├── raw/
│   │   └── Titanic-Dataset.csv       # Dataset brut
│   └── titanic_cleaned_dataset.csv   # Dataset nettoyé
│
├── models/                           # Modèles ML sauvegardés
│
├── reports/                          # Rapports Evidently générés (HTML)
│
├── scripts/                          # Scripts utilitaires
│   ├── simuler_predictions.py        # Génère 10 prédictions aléatoires
│   ├── generer_rapport_test.py       # Rapport Evidently avec données test
│   └── generer_rapport_avec_predictions.py  # Rapport avec prédictions réelles
│
├── tests/                            # Tests unitaires et d'intégration
│   └── test_api.py                   # Tests de l'API
│
├── requirements.txt                  # Dépendances Python
├── docker-compose.yml                # Orchestration Docker
└── README.md                         # Ce fichier
```

---

## Configuration

### Configuration de l'API

L'API FastAPI est configurée dans `api/main.py` avec:
- **Port** : 8000
- **Environnement** : Production (défini dans `docker-compose.yml`)
- **Health check** : Endpoint `/health` vérifié toutes les 30s par Docker
- **Logging** : Logs sauvegardés dans `logs/api.log` (rotation à 500 MB)

### Configuration Prometheus

Fichier: `prometheus/prometheus.yml`

- **Intervalle de scraping** : 15 secondes
- **Cibles** :
  - `api:8000/metrics` : Métriques de l'API
  - `prometheus:9090` : Métriques internes Prometheus
  - `cadvisor:8080` : Métriques des conteneurs

### Configuration Grafana

Fichier: `grafana/datasources/datasources.yml`

- **Datasource principale** : Prometheus (`prometheus:9090`)
- **Identifiants par défaut** : admin / admin
- **Provisioning** : Datasources et dashboards chargés automatiquement au démarrage

### Métriques Prometheus personnalisées

Toutes les métriques ML sont définies dans `api/metrics/monitoring.py`:

| Métrique | Type | Description |
|----------|------|-------------|
| `ml_predictions_total` | Counter | Nombre total de prédictions par version et classe |
| `ml_prediction_latency_seconds` | Histogram | Latence des prédictions en secondes |
| `ml_prediction_errors_total` | Counter | Erreurs de prédiction par type |
| `ml_prediction_confidence` | Gauge | Confiance moyenne par classe |
| `ml_prediction_confidence_summary` | Summary | Statistiques de confiance (quantiles) |
| `ml_data_drift_detected_total` | Counter | Drift détecté par feature |
| `ml_data_drift_score` | Gauge | Score global de drift (0-1) |
| `ml_model_accuracy` | Gauge | Précision actuelle du modèle (0-1) |
| `ml_monitoring_requests_total` | Counter | Requêtes de monitoring |

### Réseau Docker

Tous les services communiquent via le réseau bridge `ml-monitoring`. Les conteneurs peuvent se joindre par leur nom de service:
- `api` : API FastAPI
- `prometheus` : Serveur Prometheus
- `grafana` : Interface Grafana
- `cadvisor` : Monitoring des conteneurs

### Volumes persistants

- `prometheus_data` : Stockage des métriques Prometheus
- `grafana_data` : Configuration et dashboards Grafana
- Volumes montés depuis l'hôte :
  - `./models` : Modèles ML
  - `./reports` : Rapports Evidently
  - `./data` : Datasets

---

## Développement local

### Développement sans Docker

Si vous voulez développer l'API localement sans Docker:

```bash
# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'API avec hot-reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera accessible sur http://localhost:8000 avec rechargement automatique à chaque modification.

### Exécuter les tests

```bash
# Installer les dépendances de test (si pas déjà fait)
pip install pytest pytest-asyncio httpx

# Exécuter tous les tests
pytest tests/

# Tests avec verbosité
pytest tests/ -v

# Tests avec coverage
pytest tests/ --cov=api
```

### Consulter les logs

```bash
# Logs de tous les services
docker-compose logs

# Logs d'un service spécifique
docker-compose logs api
docker-compose logs prometheus
docker-compose logs grafana
docker-compose logs cadvisor

# Suivre les logs en temps réel
docker-compose logs -f api
```

### Redémarrer les services

```bash
# Redémarrer tous les services
docker-compose restart

# Redémarrer un service spécifique
docker-compose restart api

# Arrêter tous les services
docker-compose stop

# Supprimer les conteneurs (garde les volumes)
docker-compose down

# Supprimer tout (conteneurs + volumes + réseau)
docker-compose down -v
```

### Reconstruire après modifications

```bash
# Reconstruire et redémarrer l'API
docker-compose up -d --build api

# Reconstruire tous les services
docker-compose up -d --build
```

---

## Dépannage

### Problème : Les ports sont déjà utilisés

**Erreur** : `Bind for 0.0.0.0:3000 failed: port is already allocated`

**Solution** :
```bash
# Trouver le processus qui utilise le port
lsof -i :3000  # Remplacer 3000 par le port concerné

# Arrêter le processus ou changer le port dans docker-compose.yml
```

### Problème : Les conteneurs ne démarrent pas

**Erreur** : Un ou plusieurs conteneurs sont en état "Exited"

**Solution** :
```bash
# Voir les logs du conteneur en erreur
docker-compose logs api

# Vérifier l'état de tous les conteneurs
docker-compose ps

# Redémarrer complètement
docker-compose down
docker-compose up -d --build
```

### Problème : Grafana ne montre pas de données

**Causes possibles** :
1. Aucune prédiction n'a été effectuée
2. Prometheus ne scrappe pas l'API
3. La datasource n'est pas configurée

**Solution** :
```bash
# 1. Générer des données de test
python scripts/simuler_predictions.py

# 2. Vérifier que Prometheus scrappe l'API
# Aller sur http://localhost:9090/targets
# Les 3 targets (api, prometheus, cadvisor) doivent être "UP"

# 3. Vérifier la datasource dans Grafana
# Aller sur http://localhost:3000/datasources
# "Prometheus" doit être configuré avec l'URL http://prometheus:9090
```

### Problème : L'API ne répond pas

**Solution** :
```bash
# Vérifier que le conteneur est en cours d'exécution
docker-compose ps api

# Vérifier les logs
docker-compose logs api

# Tester le healthcheck
curl http://localhost:8000/health

# Redémarrer l'API
docker-compose restart api
```

### Problème : Erreur "Permission denied" lors du démarrage

**Solution** :
```bash
# S'assurer que l'utilisateur est dans le groupe docker
sudo usermod -aG docker $USER

# Se déconnecter et se reconnecter pour appliquer les changements
# Ou redémarrer le service Docker
sudo systemctl restart docker
```

### Problème : Volumes pleins ou données corrompues

**Solution** :
```bash
# Supprimer tous les volumes (ATTENTION: supprime toutes les données)
docker-compose down -v

# Recréer les services
docker-compose up -d --build
```

### Ressources utiles

- **Documentation FastAPI** : https://fastapi.tiangolo.com/
- **Documentation Prometheus** : https://prometheus.io/docs/
- **Documentation Grafana** : https://grafana.com/docs/
- **Documentation Evidently** : https://docs.evidentlyai.com/
- **Documentation Docker Compose** : https://docs.docker.com/compose/

---

## Commandes rapides

```bash
# Démarrage
docker-compose up -d --build

# Vérification
docker-compose ps
curl http://localhost:8000/health

# Générer des prédictions de test
python scripts/simuler_predictions.py

# Consulter les logs
docker-compose logs -f api

# Redémarrage
docker-compose restart

# Arrêt
docker-compose down

# Nettoyage complet (supprime les volumes)
docker-compose down -v
```