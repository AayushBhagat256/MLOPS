import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "documentation" in data


def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert "app_version" in data


def test_single_prediction_setosa(client):
    payload = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "prediction" in data
    assert data["prediction"]["predicted_class_name"] == "setosa"
    assert data["prediction"]["predicted_class_id"] == 0
    assert 0.0 <= data["prediction"]["confidence"] <= 1.0
    assert "latency_ms" in data
    assert "X-Process-Time-Sec" in response.headers


def test_single_prediction_virginica(client):
    payload = {
        "sepal_length": 6.9,
        "sepal_width": 3.1,
        "petal_length": 5.4,
        "petal_width": 2.1,
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["prediction"]["predicted_class_name"] == "virginica"
    assert data["prediction"]["predicted_class_id"] == 2


def test_validation_error_negative_feature(client):
    payload = {
        "sepal_length": -1.0,  # Invalid: gt 0.0
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422  # Unprocessable Entity


def test_validation_error_missing_field(client):
    payload = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        # Missing petal_length and petal_width
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422


def test_batch_prediction(client):
    payload = {
        "inputs": [
            {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2},
            {"sepal_length": 6.2, "sepal_width": 2.8, "petal_length": 4.8, "petal_width": 1.8},
        ]
    }
    response = client.post("/api/v1/predict-batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total_samples"] == 2
    assert len(data["predictions"]) == 2
    assert "latency_ms" in data
