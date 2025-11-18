"""
API FastAPI pour le monitoring ML du modèle Titanic.
Cette API expose des endpoints de prédiction et de monitoring.
"""

from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from loguru import logger
import time
from typing import Dict

# Import des fonctions de monitoring
from api.metrics import (
    enregistrer_prediction,
    enregistrer_erreur,
    obtenir_statistiques_metriques,
    mettre_a_jour_accuracy,
)

# Configuration de l'application FastAPI
app = FastAPI(
    title="Titanic ML Monitoring API",
    description="API de monitoring pour le modèle de prédiction de survie Titanic",
    version="1.0.0"
)

# Instrumentation Prometheus
Instrumentator().instrument(app).expose(app)

# Configuration du logger
logger.add("logs/api.log", rotation="500 MB", level="INFO")


# ============================================================
# ENDPOINTS PRINCIPAUX
# ============================================================

@app.get("/")
def root() -> Dict:
    """
    Endpoint racine de l'API.

    Returns:
        Message de bienvenue et informations sur l'API
    """
    return {
        "message": "API de Monitoring ML Titanic en ligne",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "metrics": "/metrics",
            "health": "/health",
            "stats": "/monitoring/stats"
        }
    }


@app.get("/health")
def health_check() -> Dict:
    """
    Endpoint de vérification de santé pour Docker healthcheck.

    Returns:
        Statut de l'API
    """
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


# ============================================================
# ENDPOINTS DE MONITORING
# ============================================================

@app.get("/monitoring/stats")
def obtenir_stats() -> Dict:
    """
    Récupère les statistiques de monitoring actuelles.

    Returns:
        Statistiques des métriques Prometheus
    """
    try:
        stats = obtenir_statistiques_metriques()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des stats: {e}")
        enregistrer_erreur("stats_error")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/monitoring/test/prediction")
def test_enregistrer_prediction(
    model_version: str = "v1.0",
    prediction_class: str = "survived",
    confidence: float = 0.85
) -> Dict:
    """
    Endpoint de test pour enregistrer une prédiction.

    Args:
        model_version: Version du modèle
        prediction_class: Classe prédite (survived/not_survived)
        confidence: Niveau de confiance (0-1)

    Returns:
        Confirmation de l'enregistrement
    """
    try:
        # Simuler un temps de traitement
        start_time = time.time()
        time.sleep(0.01)  # Simuler le temps de prédiction
        latency = time.time() - start_time

        # Enregistrer la prédiction dans Prometheus
        enregistrer_prediction(
            model_version=model_version,
            prediction_class=prediction_class,
            confidence=confidence,
            latency=latency
        )

        return {
            "status": "success",
            "message": "Prédiction enregistrée",
            "data": {
                "model_version": model_version,
                "prediction_class": prediction_class,
                "confidence": confidence,
                "latency": latency
            }
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement de la prédiction: {e}")
        enregistrer_erreur("prediction_test_error")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/monitoring/test/accuracy")
def test_mettre_a_jour_accuracy(
    model_version: str = "v1.0",
    accuracy: float = 0.82
) -> Dict:
    """
    Endpoint de test pour mettre à jour l'accuracy du modèle.

    Args:
        model_version: Version du modèle
        accuracy: Précision du modèle (0-1)

    Returns:
        Confirmation de la mise à jour
    """
    try:
        # Valider l'accuracy
        if not 0 <= accuracy <= 1:
            raise ValueError("L'accuracy doit être entre 0 et 1")

        # Mettre à jour la métrique
        mettre_a_jour_accuracy(
            model_version=model_version,
            accuracy=accuracy
        )

        return {
            "status": "success",
            "message": "Accuracy mise à jour",
            "data": {
                "model_version": model_version,
                "accuracy": accuracy
            }
        }
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de l'accuracy: {e}")
        enregistrer_erreur("accuracy_test_error")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# ÉVÉNEMENTS DE DÉMARRAGE ET ARRÊT
# ============================================================

@app.on_event("startup")
async def startup_event():
    """
    Événement exécuté au démarrage de l'application.
    """
    logger.info("Démarrage de l'API Titanic ML Monitoring")
    logger.info("Instrumentation Prometheus activée")
    logger.info("Endpoints de monitoring disponibles")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Événement exécuté à l'arrêt de l'application.
    """
    logger.info("Arrêt de l'API Titanic ML Monitoring")
