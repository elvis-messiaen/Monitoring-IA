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

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/elvis-messiaen/Monitoring-IA.git
   cd Monitoring-IA
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Verify services are running**
   ```bash
   docker-compose ps
   ```

### Access Points

- **API Documentation**: http://localhost:8000/docs
- **Grafana Dashboard**: http://localhost:3000
  - Username: `admin`
  - Password: `admin`
- **Prometheus**: http://localhost:9090
- **cAdvisor**: http://localhost:8080

## 📁 Project Structure

```
Monitoring-IA/
├── api/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration (empty placeholder)
│   ├── models.py            # ML models definitions (placeholder)
│   ├── predict.py           # Prediction endpoints (to implement)
│   ├── monitoring.py        # Custom monitoring metrics (to implement)
│   └── Dockerfile           # Docker configuration for API
├── grafana/
│   ├── datasources/
│   │   └── prometheus.yml   # Grafana datasource configuration
│   └── dashboards/          # Grafana dashboard definitions
├── prometheus/
│   └── prometheus.yml       # Prometheus scraping configuration
├── notebooks/
│   ├── 01_data_exploration.ipynb  # Data analysis notebook
│   └── 02_model_training.ipynb    # Model training notebook
├── data/
│   ├── raw/Titanic-Dataset.csv   # Raw Titanic dataset
│   └── titanic_cleaned_dataset.csv # Cleaned dataset
├── models/                # ML model artifacts
├── reports/               # Model reports and metrics
├── scripts/               # Utility scripts
├── tests/                 # Test suite
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker orchestration
└── README.md             # This file
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

## 📊 Available Features

### API Endpoints

- `GET /`: Root endpoint - API status
- `GET /metrics`: Prometheus metrics
- `GET /docs`: Interactive API documentation
- `GET /health`: Health check endpoint

### Monitoring Metrics

- **HTTP Requests**: Request count, latency, error rates
- **System Metrics**: CPU, memory, disk usage (via cAdvisor)
- **Application Metrics**: Custom ML metrics (to be implemented)
- **Container Metrics**: Resource usage per container

### Dashboards

- **System Overview**: Overall system health and performance
- **API Performance**: Request metrics and response times
- **Container Monitoring**: Resource usage and health
- **ML Model Metrics** (planned): Model performance and data drift

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
# View Prometheus metrics
curl http://localhost:9090/metrics

# View API metrics
curl http://localhost:8000/metrics
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