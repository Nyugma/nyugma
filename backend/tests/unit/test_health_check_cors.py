"""
Unit tests for health check endpoint CORS and frontend URL configuration.

Requirements: 6.8 - CORS configuration in health status
"""

import pytest
import os
from fastapi.testclient import TestClient


class TestHealthCheckCORSConfiguration:
    """Test suite for health check endpoint CORS configuration."""
    
    def test_health_check_includes_cors_component(self):
        """Test that health check includes CORS component status."""
        # Import app fresh to get current environment
        from src.api.main import app
        client = TestClient(app)
        
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify CORS component is present
        assert "components" in data
        assert "cors" in data["components"]
        assert data["components"]["cors"] in ["configured", "development_mode"]
    
    def test_health_check_includes_cors_origins_in_statistics(self):
        """Test that health check includes CORS origins in statistics."""
        from src.api.main import app
        client = TestClient(app)
        
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify CORS origins are present in statistics
        assert "statistics" in data
        assert "cors_origins" in data["statistics"]
        assert isinstance(data["statistics"]["cors_origins"], str)
    
    def test_health_check_includes_frontend_url_in_statistics(self):
        """Test that health check includes frontend URL in statistics."""
        from src.api.main import app
        client = TestClient(app)
        
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify frontend URL is present in statistics
        assert "statistics" in data
        assert "frontend_url" in data["statistics"]
        assert isinstance(data["statistics"]["frontend_url"], str)
    
    def test_cors_component_shows_development_mode_for_wildcard(self):
        """Test that CORS component shows 'development_mode' when CORS_ORIGINS is '*'."""
        # Set environment to wildcard
        original_cors = os.environ.get("CORS_ORIGINS")
        os.environ["CORS_ORIGINS"] = "*"
        
        try:
            # Need to reload the module to pick up new environment
            import importlib
            import src.api.main
            importlib.reload(src.api.main)
            from src.api.main import app
            
            client = TestClient(app)
            response = client.get("/api/health")
            
            assert response.status_code == 200
            data = response.json()
            
            # Should show development_mode for wildcard
            assert data["components"]["cors"] == "development_mode"
            assert data["statistics"]["cors_origins"] == "*"
        finally:
            # Restore original environment
            if original_cors is not None:
                os.environ["CORS_ORIGINS"] = original_cors
            elif "CORS_ORIGINS" in os.environ:
                del os.environ["CORS_ORIGINS"]
    
    def test_cors_component_shows_configured_for_specific_origins(self):
        """Test that CORS component shows 'configured' when specific origins are set."""
        # Set environment to specific origins
        original_cors = os.environ.get("CORS_ORIGINS")
        os.environ["CORS_ORIGINS"] = "https://example.com,https://frontend.app"
        
        try:
            # Need to reload the module to pick up new environment
            import importlib
            import src.api.main
            importlib.reload(src.api.main)
            from src.api.main import app
            
            client = TestClient(app)
            response = client.get("/api/health")
            
            assert response.status_code == 200
            data = response.json()
            
            # Should show configured for specific origins
            assert data["components"]["cors"] == "configured"
            assert data["statistics"]["cors_origins"] == "https://example.com,https://frontend.app"
        finally:
            # Restore original environment
            if original_cors is not None:
                os.environ["CORS_ORIGINS"] = original_cors
            elif "CORS_ORIGINS" in os.environ:
                del os.environ["CORS_ORIGINS"]
    
    def test_frontend_url_shows_not_configured_when_not_set(self):
        """Test that frontend URL shows 'not_configured' when environment variable is not set."""
        # Ensure FRONTEND_URL is not set
        original_frontend = os.environ.get("FRONTEND_URL")
        if "FRONTEND_URL" in os.environ:
            del os.environ["FRONTEND_URL"]
        
        try:
            # Need to reload the module to pick up new environment
            import importlib
            import src.api.main
            importlib.reload(src.api.main)
            from src.api.main import app
            
            client = TestClient(app)
            response = client.get("/api/health")
            
            assert response.status_code == 200
            data = response.json()
            
            # Should show not_configured when not set
            assert data["statistics"]["frontend_url"] == "not_configured"
        finally:
            # Restore original environment
            if original_frontend is not None:
                os.environ["FRONTEND_URL"] = original_frontend
    
    def test_frontend_url_shows_configured_value_when_set(self):
        """Test that frontend URL shows the configured value when environment variable is set."""
        # Set FRONTEND_URL
        original_frontend = os.environ.get("FRONTEND_URL")
        test_url = "https://my-frontend.netlify.app"
        os.environ["FRONTEND_URL"] = test_url
        
        try:
            # Need to reload the module to pick up new environment
            import importlib
            import src.api.main
            importlib.reload(src.api.main)
            from src.api.main import app
            
            client = TestClient(app)
            response = client.get("/api/health")
            
            assert response.status_code == 200
            data = response.json()
            
            # Should show the configured URL
            assert data["statistics"]["frontend_url"] == test_url
        finally:
            # Restore original environment
            if original_frontend is not None:
                os.environ["FRONTEND_URL"] = original_frontend
            elif "FRONTEND_URL" in os.environ:
                del os.environ["FRONTEND_URL"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
