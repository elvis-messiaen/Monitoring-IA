from pathlib import Path
import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "model.pkl"

pipeline = joblib.load(MODEL_PATH)


def encode_sex(sex: str) -> int:
    """
    Encode sex value to integer.

    Args:
        sex: Sex value ('M' for male, 'F' for female)

    Returns:
        0 for male, 1 for female
    """
    return 0 if sex.upper() == "M" else 1


def decode_survived(pred: int) -> str:
    """
    Decode survival prediction to human-readable string.

    Args:
        pred: Prediction value (0 or 1)

    Returns:
        'Died' if prediction is 0, 'Survived' if prediction is 1
    """
    return "Died" if pred == 0 else "Survived"


def predict_passenger(passenger: dict) -> int:
    """
    Predict the survival outcome for a single Titanic passenger.

    The input dictionary must contain:
    - "Sex": a string, either "M" for male or "F" for female.
      The value is internally converted to a numerical code:
        - "M" → 0
        - "F" → 1
    - "Fare": a float representing the ticket price paid by the passenger.

    The function encodes the input, passes it through the trained ML pipeline,
    and returns a human-readable prediction.

    Args:
        passenger: Dictionary with passenger data

    Returns:
        "Survived" if the predicted class is 1, "Died" if the predicted class is 0

    Example:
        Input:  {"Sex": "F", "Fare": 23.45}
        Output: "Survived"
    """
    passenger_encoded = passenger.copy()
    passenger_encoded["Sex"] = encode_sex(passenger["Sex"])

    df = pd.DataFrame([passenger_encoded])
    prediction = pipeline.predict(df)[0]
    return decode_survived(int(prediction))


def predict_passengers(passengers: list) -> list:
    """
    Predict the survival outcomes for multiple Titanic passengers.

    Each passenger in the list must be a dictionary containing:
    - "Sex": a string, either "M" (male) or "F" (female),
             which will be internally encoded as:
               - "M" → 0
               - "F" → 1
    - "Fare": a float representing the ticket price paid.

    The function processes the batch of passengers, applies the trained ML model,
    and returns a list of human-readable predictions.

    Args:
        passengers: List of passenger dictionaries

    Returns:
        List where each element is either "Survived" (predicted class = 1)
        or "Died" (predicted class = 0)

    Example:
        Input:
            [
                {"Sex": "M", "Fare": 10.0},
                {"Sex": "F", "Fare": 50.0}
            ]
        Output:
            ["Died", "Survived"]
    """
    passenger_encoded = []
    for p in passengers:
        passenger_encoded.append({
            "Sex": encode_sex(p["Sex"]),
            "Fare": p["Fare"]
        })

    df = pd.DataFrame(passenger_encoded)
    predictions = pipeline.predict(df)
    return [decode_survived(int(p)) for p in predictions]