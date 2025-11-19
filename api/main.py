from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from api.models import Passenger, Passengers
from api.predict import predict_passenger, predict_passengers
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

app = FastAPI(
    title="Titanic Survival API",
    version="1.1",
    description="""
    API to predict the survival of a Titanic passenger.

    - `/predict`: prediction for one passenger.

    - `/predict_many`: prediction for multiple passengers.

    The inputs must be:
    - Sex: 'M' or 'F'
    - Fare: float
    The output will be 'Died' or 'Survived'.
    """


)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.post("/predict", summary="Prediction for one Titanic passenger", response_description="Response of the prediction")
def predict(passenger: Passenger):
    """
    Predict survival for a single Titanic passenger.

    This endpoint receives the passenger's information and returns
    a human-readable prediction: "Survived" or "Died".

    Input fields:
    - Sex (string): Must be "M" for male or "F" for female.
                    The value is automatically encoded by the API.
    - Fare (float): The ticket price paid by the passenger.

    Example request:
    {
        "Sex": "F",
        "Fare": 23.45
    }

    Example response:
    {
        "prediction": "Survived"
    }
    """
    import time

    # Mesurer la latence
    start_time = time.time()

    try:
        # Faire la prediction
        prediction = predict_passenger(passenger.dict())

        # Calculer la latence
        latency = time.time() - start_time

        # Obtenir la probabilite de prediction (confiance)
        from api.predict import encode_sex, pipeline
        import pandas as pd

        passenger_encoded = passenger.dict()
        passenger_encoded["Sex"] = encode_sex(passenger.Sex)
        df = pd.DataFrame([passenger_encoded])
        proba = pipeline.predict_proba(df)[0]

        # La confiance est la probabilite maximale
        confidence = float(max(proba))

        # Enregistrer la prediction dans les metriques
        enregistrer_prediction(
            model_version="v1.0",
            prediction_class=prediction.lower(),
            confidence=confidence,
            latency=latency
        )

        return {"prediction": prediction}

    except Exception as e:
        # Enregistrer l'erreur
        enregistrer_erreur("prediction_error")
        raise


@app.post("/predict_many", summary="Prediction for multiple Titanic passengers", response_description="List of predictions")
def predict_many(passengers: Passengers):
    """
    Predict survival for multiple Titanic passengers in a single request.

    This endpoint accepts a list of passengers and returns
    a list of human-readable predictions for each one.

    Input structure:
    - Each passenger must include:
        - Sex (string): "M" (male) or "F" (female).
        - Fare (float): Ticket price.

    Example request:
    [
        {"Sex": "M", "Fare": 10.0},
        {"Sex": "F", "Fare": 50.0}
    ]

    Example response:
    {
        "predictions": [
            "Died",
            "Survived"
        ]
    }
    """
    passenger_list = [p.dict() for p in passengers.passengers]
    predictions = predict_passengers(passenger_list)
    return {"predictions": predictions}



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
