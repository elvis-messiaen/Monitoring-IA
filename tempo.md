# TEMPO.md - Guide de démarrage du monitoring ML

Date: 2025-11-18
Projet: Monitoring-IA - Système de monitoring ML pour le modèle Titanic

---

## Démarrage du système

### 1. Lancer la stack Docker

```bash
# Démarrer tous les services
docker-compose up -d --build

# Vérifier que les services sont démarrés
docker-compose ps

# Voir les logs en temps réel
docker-compose logs -f api
```

### 2. Tester l'API

```bash
# Test 1: Vérifier que l'API est en ligne
curl http://localhost:8000/health

# Test 2: Enregistrer une prédiction de test
curl -X POST "http://localhost:8000/monitoring/test/prediction?model_version=v1.0&prediction_class=survived&confidence=0.85"

# Test 3: Consulter les métriques Prometheus
curl http://localhost:8000/metrics
```

### 3. Accéder aux interfaces

- **API Documentation**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

### 4. Générer un rapport Evidently

```bash
# Generer un rapport de drift HTML
python scripts/generer_rapport_test.py

# Ouvrir le rapport genere
open reports/drift_report_test.html
```

Note: Evidently génère des rapports HTML statiques (pas une interface web en temps réel). Les rapports sont sauvegardés dans le dossier `reports/` et s'ouvrent dans votre navigateur.

---

## Métriques Prometheus disponibles

Toutes les métriques personnalisées sont opérationnelles:
- `ml_predictions_total` - Compteur de prédictions
- `ml_prediction_latency_seconds` - Latence des prédictions
- `ml_prediction_errors_total` - Compteur d'erreurs
- `ml_prediction_confidence` - Confiance moyenne
- `ml_data_drift_detected_total` - Drift détecté
- `ml_data_drift_score` - Score de drift
- `ml_model_accuracy` - Précision du modèle
- `ml_monitoring_requests_total` - Requêtes de monitoring

---

## Endpoints API disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Informations sur l'API |
| `/health` | GET | Healthcheck Docker |
| `/metrics` | GET | Métriques Prometheus |
| `/docs` | GET | Documentation Swagger |
| `/monitoring/stats` | GET | Statistiques de monitoring |
| `/monitoring/test/prediction` | POST | Test d'enregistrement de prédiction |
| `/monitoring/test/accuracy` | POST | Test de mise à jour d'accuracy |

---

## Arrêt et maintenance

```bash
# Arrêter les services
docker-compose down

# Nettoyer complètement (supprime les volumes)
docker-compose down -v

# Voir les logs d'un service spécifique
docker-compose logs prometheus
docker-compose logs grafana
```

---

## Résolution de problèmes

### Les services ne démarrent pas
```bash
# Vérifier les ports disponibles
lsof -i :8000  # API
lsof -i :9090  # Prometheus
lsof -i :3000  # Grafana

# Reconstruire les images
docker-compose up -d --build --force-recreate
```

### Les métriques n'apparaissent pas
```bash
# Vérifier que l'API expose bien /metrics
curl http://localhost:8000/metrics

# Vérifier les targets dans Prometheus
open http://localhost:9090/targets
```

---

**Document créé le:** 2025-11-18
**Version:** 1.0
**Statut:** Système opérationnel ✅