# Monitoring-IA

A comprehensive Machine Learning monitoring solution that combines Titanic prediction models with real-time monitoring using Prometheus, Grafana, and Docker.

## 📋 Overview

This project implements a complete ML monitoring pipeline for a Titanic survival prediction model. It includes:
- FastAPI-based REST API for ML predictions
- Real-time monitoring and metrics collection with Prometheus
- Interactive dashboards with Grafana (API Performance + ML Metrics)
- ML model drift detection and performance monitoring with Evidently AI
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

### Making Predictions

```bash
# Single prediction
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"Sex": "F", "Fare": 30.0}'

# Batch predictions
curl -X POST "http://localhost:8000/predict_many" \
  -H "Content-Type: application/json" \
  -d '{"passengers": [{"Sex": "M", "Fare": 10.0}, {"Sex": "F", "Fare": 50.0}]}'
```

### Generate Evidently Reports

```bash
# Install dependencies (if local development)
pip install -r requirements.txt

# Generate drift report (sample data)
python scripts/generer_rapport_test.py

# Generate report with real model predictions
python scripts/generer_rapport_avec_predictions.py

# Open the report
open reports/drift_report_with_predictions_*.html
```

### Visualize Metrics and Monitoring

#### 🎯 Step 1: Generate Prediction Data

Before viewing dashboards, generate some prediction data:

```bash
# Run 10 random predictions to populate metrics
python scripts/simuler_predictions.py

# Or make predictions via API
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"Sex": "F", "Fare": 30.0}'
```

#### 📊 Step 2: View Grafana Dashboards

**Access Grafana**: http://localhost:3000
- **Username**: admin
- **Password**: admin

**Available Dashboards**:

1. **ML Metrics Dashboard** - http://localhost:3000/d/ml-metrics
   - Predictions by class (increase over time)
   - Prediction latency (p50, p95, p99)
   - Model accuracy gauge (0-1 scale)
   - Data drift score gauge
   - Prediction confidence levels
   - Prediction error rates

2. **API Performance Dashboard** - http://localhost:3000/d/api-performance
   - HTTP request latency (p50, p95)
   - Requests per second
   - HTTP error rates (4xx/5xx)
   - Container CPU & RAM usage

**Dashboard Tips**:
- Set time range to **"Last 15 minutes"** to see recent data
- Enable auto-refresh (10s) for real-time updates
- Click on any panel to explore queries and customize

#### 🔍 Step 3: Query Prometheus Directly

**Access Prometheus**: http://localhost:9090

**Useful Queries**:

```promql
# Total predictions by class
ml_predictions_total

# Prediction rate (predictions per second)
rate(ml_predictions_total[5m])

# Average prediction latency
rate(ml_prediction_latency_seconds_sum[5m]) / rate(ml_prediction_latency_seconds_count[5m])

# Model accuracy
ml_model_accuracy

# Data drift score
ml_data_drift_score

# Prediction confidence by class
ml_prediction_confidence

# HTTP request rate
rate(http_requests_total[5m])

# HTTP request latency (95th percentile)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

#### 📈 Step 4: View Raw Metrics

**Access API Metrics**: http://localhost:8000/metrics

This endpoint exposes all Prometheus metrics in text format, including:
- Custom ML metrics (ml_*)
- HTTP metrics (http_*)
- Python/FastAPI runtime metrics
- Container metrics (via cAdvisor)

**Example Output**:
```
# HELP ml_predictions_total Nombre total de prédictions effectuées
# TYPE ml_predictions_total counter
ml_predictions_total{model_version="v1.0",prediction_class="survived"} 26.0
ml_predictions_total{model_version="v1.0",prediction_class="died"} 14.0

# HELP ml_prediction_latency_seconds Latence des prédictions en secondes
# TYPE ml_prediction_latency_seconds histogram
ml_prediction_latency_seconds_bucket{le="0.025",model_version="v1.0"} 40.0
ml_prediction_latency_seconds_sum{model_version="v1.0"} 0.52
ml_prediction_latency_seconds_count{model_version="v1.0"} 40.0
```

#### 🐳 Step 5: Monitor Container Resources

**Access cAdvisor**: http://localhost:8080

View detailed container-level metrics:
- CPU usage per container
- Memory consumption
- Network I/O
- Disk I/O

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
│   │   └── datasources.yml        # Grafana datasource configuration
│   └── dashboards/
│       ├── dashboard.yml          # Dashboard provisioning config
│       ├── api-performance.json   # API Performance dashboard
│       └── ml-metrics.json        # ML Metrics dashboard
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
│   ├── generer_rapport_test.py              # Script de génération de rapports (test)
│   ├── generer_rapport_avec_predictions.py  # Script de rapport avec prédictions réelles
│   └── simuler_predictions.py               # Script de simulation pour tests (10 prédictions)
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
- **Data source**: Prometheus (configured automatically via provisioning)

#### cAdvisor
- **Container monitoring**: Resource usage, performance metrics
- **Docker integration**: Automatic container discovery

## 📊 Fonctionnalités disponibles

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Docker healthcheck |
| `/metrics` | GET | Prometheus metrics |
| `/docs` | GET | Interactive Swagger documentation |
| `/predict` | POST | Single passenger survival prediction |
| `/predict_many` | POST | Batch predictions for multiple passengers |
| `/monitoring/stats` | GET | Monitoring statistics |
| `/monitoring/test/prediction` | POST | Test prediction recording |
| `/monitoring/test/accuracy` | POST | Test accuracy update |

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

### Grafana Dashboards

The project includes two pre-configured Grafana dashboards that are automatically provisioned on startup:

#### API Performance Dashboard (`grafana/dashboards/api-performance.json`)
Monitors the health and performance of the FastAPI application:
- **HTTP Request Latency** (p50, p95): Response time percentiles for all endpoints
- **Requests per Second**: Real-time request rate by HTTP method and handler
- **HTTP Error Rate** (4xx/5xx): Error tracking for client and server errors
- **Container Resources** (CPU & RAM): Resource usage metrics via cAdvisor

#### ML Metrics Dashboard (`grafana/dashboards/ml-metrics.json`)
Tracks machine learning model performance and predictions:
- **Predictions by Class** (rate 5m): Prediction distribution over time
- **Prediction Latency** (p50, p95, p99): Model inference time percentiles
- **Model Accuracy Gauge**: Current model accuracy (0-1 scale)
- **Data Drift Score Gauge**: Data drift detection score (0-1 scale)
- **Prediction Confidence**: Confidence levels by prediction class
- **Prediction Error Rate**: ML prediction errors by type

**Access Dashboards**: Navigate to http://localhost:3000 (admin/admin) and select dashboards from the left menu.

**Note**: Dashboards require active traffic to display metrics. Run `python scripts/simuler_predictions.py` to quickly generate test data and populate all metrics.

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

- **Alerting System**: Automated notifications for anomalies and drift detection
- **Model Versioning**: A/B testing and model comparison between versions
- **Data Quality Monitoring**: Real-time input data validation
- **Automated Evidently Reports**: Scheduled report generation (cron job)
- **Custom Business Metrics**: Domain-specific KPIs and dashboards
- **Security Enhancements**: Authentication, authorization, and API keys
- **Performance Optimization**: Caching, load balancing, and horizontal scaling
- **CI/CD Pipeline**: Automated testing and deployment

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

## ✨ Project Status

**Current Status**: Production Ready (97.7% complete)

**Implemented Features**:
- ✅ Trained Titanic survival prediction model (scikit-learn)
- ✅ FastAPI REST API with prediction endpoints
- ✅ Prometheus metrics collection and custom ML metrics
- ✅ Two Grafana dashboards (API Performance + ML Metrics)
- ✅ Evidently AI integration for drift detection
- ✅ Docker Compose orchestration
- ✅ Complete test suite
- ✅ Comprehensive documentation

**Remaining Tasks** (2.3%):
- Expose Evidently metrics to Prometheus/Grafana
- Automate Evidently report generation (cron job or endpoint)