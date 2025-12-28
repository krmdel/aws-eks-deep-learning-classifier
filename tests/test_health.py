"""
Tests for health check endpoint.
"""
import pytest


def test_root_endpoint(client):
    """Test the root endpoint returns correct message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Clothing Classification Service"


def test_health_endpoint(client):
    """Test the health endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


def test_health_endpoint_method_not_allowed(client):
    """Test that POST method is not allowed on health endpoint."""
    response = client.post("/health")
    assert response.status_code == 405  # Method Not Allowed



