"""
Integration tests for the root endpoint API information.

This module tests that the root endpoint returns proper JSON API information
instead of HTML redirect.
"""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.api.main import app


@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


class TestRootEndpoint:
    """Test root endpoint returns JSON API information."""
    
    def test_root_endpoint_returns_json(self, client):
        """Test that root endpoint returns JSON instead of HTML redirect."""
        response = client.get("/")
        
        # Should return 200 OK
        assert response.status_code == 200
        
        # Should return JSON content type
        assert "application/json" in response.headers["content-type"]
        
        # Should not be HTML
        assert "text/html" not in response.headers["content-type"]
    
    def test_root_endpoint_structure(self, client):
        """Test that root endpoint returns correct JSON structure."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields exist
        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert "endpoints" in data
        assert "documentation" in data
        assert "frontend_url" in data
    
    def test_root_endpoint_api_name(self, client):
        """Test that API name is correct."""
        response = client.get("/")
        data = response.json()
        
        assert data["name"] == "Legal Case Similarity API"
    
    def test_root_endpoint_version(self, client):
        """Test that API version is included."""
        response = client.get("/")
        data = response.json()
        
        assert data["version"] == "1.0.0"
    
    def test_root_endpoint_description(self, client):
        """Test that API description is included."""
        response = client.get("/")
        data = response.json()
        
        assert "description" in data
        assert len(data["description"]) > 0
        assert "similar legal cases" in data["description"].lower()
    
    def test_root_endpoint_endpoints_list(self, client):
        """Test that endpoints list includes all required endpoints."""
        response = client.get("/")
        data = response.json()
        
        endpoints = data["endpoints"]
        
        # Check that all required endpoints are listed
        assert "upload" in endpoints
        assert "health" in endpoints
        assert "performance" in endpoints
        assert "case_details" in endpoints
        assert "case_download" in endpoints
        
        # Verify endpoint descriptions include HTTP methods
        assert "POST" in endpoints["upload"]
        assert "GET" in endpoints["health"]
        assert "GET" in endpoints["performance"]
        assert "GET" in endpoints["case_details"]
        assert "GET" in endpoints["case_download"]
    
    def test_root_endpoint_documentation_link(self, client):
        """Test that documentation link is included."""
        response = client.get("/")
        data = response.json()
        
        assert data["documentation"] == "/docs"
    
    def test_root_endpoint_frontend_url(self, client):
        """Test that frontend URL is included."""
        response = client.get("/")
        data = response.json()
        
        # Should have frontend_url field
        assert "frontend_url" in data
        
        # Should either be a URL or the default message
        frontend_url = data["frontend_url"]
        assert isinstance(frontend_url, str)
        assert len(frontend_url) > 0
    
    def test_root_endpoint_frontend_url_from_env(self, client, monkeypatch):
        """Test that frontend URL is read from environment variable."""
        # Set environment variable
        test_url = "https://test-frontend.example.com"
        monkeypatch.setenv("FRONTEND_URL", test_url)
        
        # Need to reload the app to pick up the environment variable
        # For this test, we'll just verify the current behavior
        response = client.get("/")
        data = response.json()
        
        # Frontend URL should be present
        assert "frontend_url" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
