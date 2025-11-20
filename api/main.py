from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from api.models import Passenger, Passengers
from api.predict import predict_passenger, predict_passengers
from prometheus_fastapi_instrumentator import Instrumentator
from loguru import logger
import time
from typing import Dict

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

    start_time = time.time()

    try:
        prediction = predict_passenger(passenger.dict())
        latency = time.time() - start_time

        from api.predict import encode_sex, pipeline
        import pandas as pd

        passenger_encoded = passenger.dict()
        passenger_encoded["Sex"] = encode_sex(passenger.Sex)
        df = pd.DataFrame([passenger_encoded])
        proba = pipeline.predict_proba(df)[0]

        confidence = float(max(proba))

        enregistrer_prediction(
            model_version="v1.0",
            prediction_class=prediction.lower(),
            confidence=confidence,
            latency=latency
        )

        return {"prediction": prediction}

    except Exception as e:
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



Instrumentator().instrument(app).expose(app)
logger.add("logs/api.log", rotation="500 MB", level="INFO")


@app.get("/")
def root() -> Dict:
    """
    API root endpoint.

    Returns:
        Welcome message and API information
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
    Health check endpoint for Docker healthcheck.

    Returns:
        API status
    """
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


@app.get("/monitoring/stats")
def obtenir_stats() -> Dict:
    """
    Get current monitoring statistics.

    Returns:
        Prometheus metrics statistics
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
    Test endpoint to register a prediction.

    Args:
        model_version: Model version
        prediction_class: Predicted class (survived/not_survived)
        confidence: Confidence level (0-1)

    Returns:
        Registration confirmation
    """
    try:
        start_time = time.time()
        time.sleep(0.01)
        latency = time.time() - start_time

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


@app.post("/monitoring/calculate-accuracy")
def calculer_accuracy_reelle() -> Dict:
    """
    Automatically calculate the model's actual accuracy on the test dataset.

    Returns:
        Calculated accuracy and updated metric
    """
    try:
        from pathlib import Path
        import pandas as pd
        from sklearn.metrics import accuracy_score
        from api.predict import pipeline, encode_sex

        model_version: str = "v1.0"
        BASE_DIR = Path("/app")
        data_path = BASE_DIR / "data" / "titanic_cleaned_dataset.csv"

        if not data_path.exists():
            raise FileNotFoundError(f"Dataset introuvable: {data_path}")

        df = pd.read_csv(data_path)

        split_idx = int(len(df) * 0.7)
        test_data = df.iloc[split_idx:].copy()

        X_test = test_data[['Sex', 'Fare']].copy()
        y_test = test_data['Survived'].copy()

        if X_test['Sex'].dtype == 'object':
            X_test['Sex'] = X_test['Sex'].apply(lambda x: 0 if x.upper() == 'M' else 1)

        y_pred = pipeline.predict(X_test)
        accuracy = float(accuracy_score(y_test, y_pred))

        mettre_a_jour_accuracy(
            model_version=model_version,
            accuracy=accuracy
        )

        logger.info(f"Accuracy calculée et mise à jour: {accuracy:.4f} ({accuracy*100:.2f}%)")

        return {
            "status": "success",
            "message": "Accuracy calculée automatiquement sur le dataset de test",
            "data": {
                "model_version": model_version,
                "accuracy": accuracy,
                "accuracy_percentage": f"{accuracy*100:.2f}%",
                "test_samples": len(test_data),
                "correct_predictions": int(accuracy * len(test_data))
            }
        }

    except Exception as e:
        logger.error(f"Erreur lors du calcul de l'accuracy: {e}")
        enregistrer_erreur("accuracy_calculation_error")
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
async def startup_event():
    """
    Event executed at application startup.
    """
    logger.info("Démarrage de l'API Titanic ML Monitoring")
    logger.info("Instrumentation Prometheus activée")
    logger.info("Endpoints de monitoring disponibles")

    try:
        logger.info("Calcul automatique de l'accuracy du modèle...")
        from pathlib import Path
        import pandas as pd
        from sklearn.metrics import accuracy_score
        from api.predict import pipeline

        BASE_DIR = Path("/app")
        data_path = BASE_DIR / "data" / "titanic_cleaned_dataset.csv"

        if data_path.exists():
            df = pd.read_csv(data_path)

            split_idx = int(len(df) * 0.7)
            test_data = df.iloc[split_idx:].copy()

            X_test = test_data[['Sex', 'Fare']].copy()
            y_test = test_data['Survived'].copy()

            if X_test['Sex'].dtype == 'object':
                X_test['Sex'] = X_test['Sex'].apply(lambda x: 0 if x.upper() == 'M' else 1)

            y_pred = pipeline.predict(X_test)
            accuracy = float(accuracy_score(y_test, y_pred))

            mettre_a_jour_accuracy(model_version="v1.0", accuracy=accuracy)

            logger.info(f"✅ Accuracy calculée et initialisée: {accuracy:.4f} ({accuracy*100:.2f}%) sur {len(test_data)} échantillons")
        else:
            logger.warning(f"⚠️  Dataset introuvable: {data_path} - Accuracy non initialisée")

    except Exception as e:
        logger.error(f"❌ Erreur lors du calcul automatique de l'accuracy: {e}")



@app.on_event("shutdown")
async def shutdown_event():
    """
    Event executed at application shutdown.
    """
    logger.info("Arrêt de l'API Titanic ML Monitoring")