"""
Pytest configuration and shared fixtures.
"""
import pytest
from fastapi.testclient import TestClient
from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def sample_image_url():
    """Sample image URL for testing."""
    return "http://bit.ly/mlbookcamp-pants"


@pytest.fixture
def invalid_url():
    """Invalid URL for testing error handling."""
    return "not-a-valid-url"



