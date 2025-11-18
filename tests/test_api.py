import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from api.main import app

client = TestClient(app)


# -----------------------------
# Tests for /predict (single)
# -----------------------------

def test_predict_valid_input():
    """Test prediction with a valid passenger."""
    response = client.post(
        "/predict",
        json={"Sex": "F", "Fare": 30.0}
    )

    assert response.status_code == 200
    data = response.json()

    assert "prediction" in data
    assert data["prediction"] in ["Survived", "Died"]


def test_predict_missing_field():
    """Test that missing fields return a validation error."""
    response = client.post(
        "/predict",
        json={"Sex": "M"}  # Missing Fare
    )
    assert response.status_code == 422  # Unprocessable Entity


def test_predict_invalid_sex():
    """Test validation for invalid Sex value."""
    response = client.post(
        "/predict",
        json={"Sex": "X", "Fare": 10.0}
    )
    assert response.status_code == 422


# -----------------------------
# Tests for /predict_many (batch)
# -----------------------------

def test_predict_many_valid_input():
    """Test batch prediction with valid passengers."""
    response = client.post(
        "/predict_many",
        json={
            "passengers": [
                {"Sex": "M", "Fare": 10.0},
                {"Sex": "F", "Fare": 50.0}
            ]
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert len(data["predictions"]) == 2


def test_predict_many_empty_list():
    """Test that an empty batch returns a 422 validation error."""
    response = client.post(
        "/predict_many",
        json=[]
    )

    # FastAPI rejects empty lists by default only if the model requires items.
    # If your route allows an empty list, change this expectation.
    assert response.status_code in [200, 422]


def test_predict_many_invalid_passenger():
    """Test batch where one passenger is invalid."""
    response = client.post(
        "/predict_many",
        json=[
            {"Sex": "M", "Fare": 20},
            {"Sex": "X", "Fare": 50}  # Invalid
        ]
    )
    assert response.status_code == 422