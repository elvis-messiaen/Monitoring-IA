# Monitoring-IA

A comprehensive Machine Learning monitoring solution that combines Titanic prediction models with real-time monitoring using Prometheus, Grafana, and Docker.

## 📋 Overview

This project implements a complete ML monitoring pipeline for a Titanic survival prediction model. It includes:
- FastAPI-based REST API for ML predictions
- Real-time monitoring and metrics collection with Prometheus
- Interactive dashboards with Grafana
- Container orchestration with Docker Compose
- Container-level monitoring with cAdvisor

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Grafana   │    │ Prometheus  │    │  FastAPI    │
│   (Dashboards)   │  (Metrics)   │  │   (API)     │
│   Port 3000 │    │   Port 9090 │    │   Port 8000 │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌─────────────┐
                    │  cAdvisor   │
                    │(Container   │
                    │ Monitoring) │
                    │   Port 8080 │
                    └─────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git
- Python 3.11+ (pour développement local)

### Installation et démarrage

1. **Cloner le repository**
   ```bash
   git clone https://github.com/elvis-messiaen/Monitoring-IA.git
   cd Monitoring-IA
   ```

2. **Démarrer tous les services**
   ```bash
   docker-compose up -d --build
   ```

3. **Vérifier que les services fonctionnent**
   ```bash
   # Vérifier l'état des conteneurs
   docker-compose ps

   # Tester l'API
   curl http://localhost:8000/health

   # Tester une prédiction
   curl -X POST "http://localhost:8000/monitoring/test/prediction?model_version=v1.0&prediction_class=survived&confidence=0.85"

   # Consulter les métriques Prometheus
   curl http://localhost:8000/metrics
   ```

### Points d'accès

- **API Documentation**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health
- **Prometheus Metrics**: http://localhost:8000/metrics
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **cAdvisor**: http://localhost:8080

### Générer un rapport Evidently

```bash
# Installer les dépendances (si développement local)
pip install -r requirements.txt

# Générer un rapport de drift
python scripts/generer_rapport_test.py

# Ouvrir le rapport
open reports/drift_report_test.html
```

## 📁 Project Structure

```
Monitoring-IA/
├── api/
│   ├── main.py              # FastAPI application avec endpoints de monitoring
│   ├── metrics/
│   │   ├── __init__.py      # Exposition des fonctions de monitoring
│   │   └── monitoring.py    # Métriques Prometheus + Rapports Evidently
│   ├── config.py            # Configuration
│   ├── models.py            # ML models definitions
│   ├── predict.py           # Prediction endpoints
│   └── Dockerfile           # Docker configuration pour l'API
├── grafana/
│   ├── datasources/
│   │   └── prometheus.yml   # Configuration datasource Grafana
│   └── dashboards/          # Définitions des dashboards
├── prometheus/
│   └── prometheus.yml       # Configuration scraping Prometheus
├── notebooks/
│   ├── 01_data_exploration.ipynb  # Exploration des données
│   └── 02_model_training.ipynb    # Entraînement du modèle
├── data/
│   ├── raw/Titanic-Dataset.csv   # Dataset Titanic brut
│   └── titanic_cleaned_dataset.csv # Dataset nettoyé
├── models/                # Artéfacts ML sauvegardés
├── reports/               # Rapports Evidently générés (HTML)
├── scripts/
│   └── generer_rapport_test.py    # Script de génération de rapports
├── tests/                 # Suite de tests
├── requirements.txt       # Dépendances Python
├── docker-compose.yml     # Orchestration Docker
├── CLAUDE.md             # Guide pour Claude Code
├── tempo.md              # Guide de démarrage rapide
└── README.md             # Ce fichier
```

## 🔧 Configuration

### API Configuration

The FastAPI application is configured with:
- **Port**: 8000
- **Health check**: `/health` endpoint
- **Metrics**: `/metrics` endpoint (Prometheus integration)
- **Environment**: Production mode

### Monitoring Stack

#### Prometheus
- **Scraping interval**: 15 seconds
- **Targets**:
  - API metrics: `api:8000/metrics`
  - Prometheus self-monitoring: `prometheus:9090`
  - cAdvisor containers metrics: `cadvisor:8080`

#### Grafana
- **Admin credentials**: admin/admin
- **Data sources**:
  - Prometheus (default)
  - cAdvisor
  - Titanic-API

#### cAdvisor
- **Container monitoring**: Resource usage, performance metrics
- **Docker integration**: Automatic container discovery

## 📊 Fonctionnalités disponibles

### API Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Informations sur l'API |
| `/health` | GET | Healthcheck Docker |
| `/metrics` | GET | Métriques Prometheus |
| `/docs` | GET | Documentation Swagger interactive |
| `/monitoring/stats` | GET | Statistiques de monitoring |
| `/monitoring/test/prediction` | POST | Test d'enregistrement de prédiction |
| `/monitoring/test/accuracy` | POST | Test de mise à jour d'accuracy |

### Métriques Prometheus personnalisées

Toutes les métriques ML sont disponibles via `/metrics`:

- `ml_predictions_total` - Compteur de prédictions par version et classe
- `ml_prediction_latency_seconds` - Histogramme de latence des prédictions
- `ml_prediction_errors_total` - Compteur d'erreurs par type
- `ml_prediction_confidence` - Gauge de confiance moyenne par classe
- `ml_prediction_confidence_summary` - Statistiques de confiance
- `ml_data_drift_detected_total` - Compteur de drift détecté par feature
- `ml_data_drift_score` - Score de drift global (0-1)
- `ml_model_accuracy` - Précision actuelle du modèle
- `ml_monitoring_requests_total` - Compteur de requêtes de monitoring

### Rapports Evidently

Génération de rapports HTML interactifs pour:
- **Classification Performance**: Métriques de performance du modèle
- **Data Drift Detection**: Détection de dérive des données
- **Rapports combinés**: Classification + Drift

Les rapports sont sauvegardés dans `reports/` et s'ouvrent dans le navigateur.

### Dashboards

- **System Overview**: Santé et performance globale du système
- **API Performance**: Métriques de requêtes et temps de réponse
- **Container Monitoring**: Utilisation des ressources par conteneur
- **ML Model Metrics**: Performance du modèle et drift (via Evidently)

## 🐳 Docker Services

### API Service
```yaml
- Image: Custom build from api/Dockerfile
- Ports: 8000:8000
- Volumes: ./models, ./reports, ./data
- Health check: HTTP health endpoint
- Restart: unless-stopped
```

### Prometheus Service
```yaml
- Image: prom/prometheus:latest
- Ports: 9090:9090
- Volume: Custom prometheus.yml
- Data persistence: prometheus_data volume
- Restart: unless-stopped
```

### Grafana Service
```yaml
- Image: grafana/grafana:latest
- Ports: 3000:3000
- Volumes: Dashboard and datasource provisioning
- Environment: Admin password configuration
- Restart: unless-stopped
```

### cAdvisor Service
```yaml
- Image: gcr.io/cadvisor/cadvisor:latest
- Ports: 8080:8080
- Volumes: System mounts for container monitoring
- Restart: unless-stopped
```

## 📚 Dependencies

### Core Dependencies
- **FastAPI**: Web framework for APIs
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation

### Machine Learning
- **scikit-learn**: ML algorithms
- **pandas**: Data manipulation
- **numpy**: Numerical operations
- **seaborn**: Data visualization
- **matplotlib**: Plotting

### Monitoring
- **prometheus-client**: Prometheus metrics client
- **prometheus-fastapi-instrumentator**: FastAPI integration
- **evidently**: ML monitoring and drift detection

### Utilities
- **python-multipart**: File uploads
- **python-dotenv**: Environment variables
- **loguru**: Logging
- **pytest**: Testing framework

## 🔍 Development

### Running Tests
```bash
pytest tests/
```

### Development Mode
```bash
# Install dependencies
pip install -r requirements.txt

# Run API locally
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Monitoring Development

```bash
# Voir les métriques Prometheus
curl http://localhost:9090/metrics

# Voir les métriques API personnalisées
curl http://localhost:8000/metrics

# Générer un rapport Evidently
python scripts/generer_rapport_test.py

# Tester l'enregistrement de prédictions
curl -X POST "http://localhost:8000/monitoring/test/prediction?model_version=v1.0&prediction_class=survived&confidence=0.85"

# Tester la mise à jour d'accuracy
curl -X POST "http://localhost:8000/monitoring/test/accuracy?model_version=v1.0&accuracy=0.82"
```

### Utiliser les fonctions de monitoring dans votre code

```python
from api.metrics import (
    enregistrer_prediction,
    enregistrer_erreur,
    mettre_a_jour_accuracy,
    generer_rapport_drift,
    generer_rapport_complet
)

# Enregistrer une prédiction
enregistrer_prediction(
    model_version="v1.0",
    prediction_class="survived",
    confidence=0.85,
    latency=0.023
)

# Générer un rapport de drift
import pandas as pd

reference_data = pd.read_csv('data/titanic_cleaned_dataset.csv')
current_data = pd.read_csv('data/new_data.csv')

rapport = generer_rapport_drift(
    reference_data=reference_data,
    current_data=current_data,
    output_path='reports/drift_report.html'
)
```

## 📈 Future Enhancements

- **ML Model Integration**: Complete Titanic prediction model
- **Custom Metrics**: Business-specific KPIs
- **Alerting**: Automated notifications for anomalies
- **Model Versioning**: A/B testing and model comparison
- **Data Quality Monitoring**: Input data validation
- **Model Drift Detection**: Automated performance tracking
- **Security Enhancements**: Authentication and authorization
- **Performance Optimization**: Caching and load balancing

## 🛠️ Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000, 8000, 8080, 9090 are available
2. **Docker permissions**: Ensure user has Docker permissions
3. **Resource limits**: Monitor system resources with `docker stats`

### Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs api
docker-compose logs prometheus
docker-compose logs grafana
```

### Reset Services

```bash
# Stop and remove all containers
docker-compose down

# Remove volumes (note: this deletes all data)
docker-compose down -v

# Rebuild and restart
docker-compose up -d --build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions and support:
- Create an issue in the GitHub repository
- Check the documentation at `/docs` endpoint
- Review Grafana dashboards for system insights

---

**Note**: This is an ML monitoring project focusing on infrastructure setup. The actual machine learning model and advanced monitoring features are currently being developed.