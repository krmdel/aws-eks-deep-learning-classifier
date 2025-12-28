"""
Integration tests for the clothing classification service.
"""
import pytest


def test_full_workflow(client, sample_image_url):
    """Test the complete workflow from health check to prediction."""
    # Step 1: Check service is healthy
    health_response = client.get("/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "healthy"
    
    # Step 2: Make a prediction
    request_data = {"url": sample_image_url}
    predict_response = client.post("/predict", json=request_data)
    
    assert predict_response.status_code == 200
    result = predict_response.json()
    
    # Step 3: Verify prediction result
    assert "top_class" in result
    assert "top_probability" in result
    assert result["top_probability"] > 0
    
    # Step 4: Verify we can make multiple predictions
    predict_response_2 = client.post("/predict", json=request_data)
    assert predict_response_2.status_code == 200


def test_multiple_predictions_consistency(client, sample_image_url):
    """Test that multiple predictions for the same image are consistent."""
    request_data = {"url": sample_image_url}
    
    # Make first prediction
    response1 = client.post("/predict", json=request_data)
    assert response1.status_code == 200
    result1 = response1.json()
    
    # Make second prediction
    response2 = client.post("/predict", json=request_data)
    assert response2.status_code == 200
    result2 = response2.json()
    
    # Results should be identical (deterministic model)
    assert result1["top_class"] == result2["top_class"]
    assert abs(result1["top_probability"] - result2["top_probability"]) < 1e-6
    
    # All probabilities should match
    for class_name in result1["predictions"]:
        assert abs(
            result1["predictions"][class_name] - 
            result2["predictions"][class_name]
        ) < 1e-6


def test_different_images(client):
    """Test predictions with different image URLs."""
    test_urls = [
        "http://bit.ly/mlbookcamp-pants",
        # Add more test URLs if available
    ]
    
    for url in test_urls:
        request_data = {"url": url}
        response = client.post("/predict", json=request_data)
        
        assert response.status_code == 200
        result = response.json()
        
        assert "top_class" in result
        assert "top_probability" in result
        assert result["top_probability"] > 0



