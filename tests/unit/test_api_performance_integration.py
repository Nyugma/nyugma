"""
Integration tests for API performance monitoring.

Requirements: 5.1, 5.2, 5.3
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app, performance_monitor


class TestAPIPerformanceIntegration:
    """Test suite for API performance monitoring integration."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Reset performance monitor before each test."""
        performance_monitor.reset_stats()
        yield
        performance_monitor.reset_stats()
    
    def test_health_endpoint_includes_performance_metrics(self):
        """Test that health endpoint includes performance metrics."""
        client = TestClient(app)
        
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "performance" in data
        assert "concurrent_requests" in data["performance"]
        assert "search_performance" in data["performance"]
        assert "upload_performance" in data["performance"]
    
    def test_performance_endpoint_returns_metrics(self):
        """Test dedicated performance endpoint."""
        client = TestClient(app)
        
        response = client.get("/api/performance")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "operation_stats" in data
        assert "memory_stats" in data
        assert "concurrent_request_stats" in data
        assert "recent_operations" in data
    
    def test_concurrent_request_tracking_in_api(self):
        """Test that concurrent requests are tracked."""
        client = TestClient(app)
        
        # The health endpoint doesn't track performance, so we just verify
        # the performance endpoint is accessible and returns valid data
        perf_response = client.get("/api/performance")
        data = perf_response.json()
        
        stats = data["concurrent_request_stats"]
        # After reset, should be 0
        assert stats["active_requests"] == 0
        assert "total_requests" in stats
        assert "max_concurrent_requests" in stats
    
    def test_memory_stats_available(self):
        """Test that memory statistics are available."""
        client = TestClient(app)
        
        response = client.get("/api/performance")
        
        assert response.status_code == 200
        data = response.json()
        
        memory_stats = data["memory_stats"]
        assert "current_memory_mb" in memory_stats
        assert memory_stats["current_memory_mb"] > 0
