from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from api.models import Passenger, Passengers
from api.predict import predict_passenger, predict_passengers
from prometheus_fastapi_instrumentator import Instrumentator

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
    prediction = predict_passenger(passenger.dict())
    return {"prediction": prediction}


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
