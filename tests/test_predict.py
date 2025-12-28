"""
Tests for prediction endpoint.
"""
import pytest


def test_predict_endpoint_success(client, sample_image_url):
    """Test successful prediction request."""
    request_data = {"url": sample_image_url}
    
    response = client.post("/predict", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "predictions" in data
    assert "top_class" in data
    assert "top_probability" in data
    
    # Check predictions is a dict with all classes
    assert isinstance(data["predictions"], dict)
    assert len(data["predictions"]) == 10
    
    # Check all expected classes are present
    expected_classes = [
        "dress", "hat", "longsleeve", "outwear", "pants",
        "shirt", "shoes", "shorts", "skirt", "t-shirt"
    ]
    for cls in expected_classes:
        assert cls in data["predictions"]
        assert isinstance(data["predictions"][cls], float)
        assert 0 <= data["predictions"][cls] <= 1
    
    # Check top_class is one of the expected classes
    assert data["top_class"] in expected_classes
    
    # Check top_probability is a float between 0 and 1
    assert isinstance(data["top_probability"], float)
    assert 0 <= data["top_probability"] <= 1
    
    # Check top_probability matches the prediction for top_class
    assert abs(data["top_probability"] - data["predictions"][data["top_class"]]) < 1e-6


def test_predict_endpoint_missing_url(client):
    """Test prediction request with missing URL."""
    response = client.post("/predict", json={})
    
    assert response.status_code == 422  # Unprocessable Entity
    assert "detail" in response.json()


def test_predict_endpoint_invalid_url(client):
    """Test prediction request with invalid URL."""
    request_data = {"url": "not-a-valid-url"}
    
    response = client.post("/predict", json=request_data)
    
    # Should return 422 for invalid URL format
    assert response.status_code == 422
    assert "detail" in response.json()


def test_predict_endpoint_wrong_method(client, sample_image_url):
    """Test that GET method is not allowed on predict endpoint."""
    response = client.get("/predict")
    assert response.status_code == 405  # Method Not Allowed


def test_predict_endpoint_empty_body(client):
    """Test prediction request with empty body."""
    response = client.post("/predict", json=None)
    
    assert response.status_code == 422


def test_predict_endpoint_invalid_json(client):
    """Test prediction request with invalid JSON."""
    response = client.post(
        "/predict",
        data="invalid json",
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 422


def test_predict_probabilities_sum(client, sample_image_url):
    """Test that prediction probabilities are reasonable (softmax-like)."""
    request_data = {"url": sample_image_url}
    
    response = client.post("/predict", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Sum of probabilities should be close to 1.0 (softmax)
    prob_sum = sum(data["predictions"].values())
    assert abs(prob_sum - 1.0) < 0.01  # Allow small floating point errors


def test_predict_response_model(client, sample_image_url):
    """Test that response matches the PredictResponse model."""
    request_data = {"url": sample_image_url}
    
    response = client.post("/predict", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify all required fields are present and correct types
    assert isinstance(data["predictions"], dict)
    assert isinstance(data["top_class"], str)
    assert isinstance(data["top_probability"], float)

