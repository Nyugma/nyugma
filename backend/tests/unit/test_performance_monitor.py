"""
Unit tests for the PerformanceMonitor component.

Requirements: 5.1, 5.2, 5.3
"""

import time
import pytest
from src.components.performance_monitor import PerformanceMonitor, get_performance_monitor


class TestPerformanceMonitor:
    """Test suite for PerformanceMonitor."""
    
    def test_track_operation_basic(self):
        """Test basic operation tracking."""
        monitor = PerformanceMonitor()
        
        with monitor.track_operation("test_operation"):
            time.sleep(0.1)  # Simulate work
        
        stats = monitor.get_operation_stats("test_operation")
        assert stats["count"] == 1
        assert stats["avg_duration"] >= 0.1
        assert stats["success_rate"] == 1.0
    
    def test_track_operation_with_metadata(self):
        """Test operation tracking with metadata."""
        monitor = PerformanceMonitor()
        
        metadata = {"test_key": "test_value"}
        with monitor.track_operation("test_operation", metadata=metadata):
            pass
        
        recent = monitor.get_recent_operations(limit=1)
        assert len(recent) == 1
        assert recent[0]["metadata"] == metadata
    
    def test_track_operation_failure(self):
        """Test operation tracking when operation fails."""
        monitor = PerformanceMonitor()
        
        try:
            with monitor.track_operation("failing_operation"):
                raise ValueError("Test error")
        except ValueError:
            pass
        
        stats = monitor.get_operation_stats("failing_operation")
        assert stats["count"] == 1
        assert stats["success_rate"] == 0.0
        assert stats["total_failures"] == 1
    
    def test_concurrent_request_tracking(self):
        """Test concurrent request tracking."""
        monitor = PerformanceMonitor()
        
        # Simulate concurrent requests
        with monitor.track_operation("request_1"):
            with monitor.track_operation("request_2"):
                concurrent_stats = monitor.get_concurrent_request_stats()
                assert concurrent_stats["active_requests"] == 2
        
        final_stats = monitor.get_concurrent_request_stats()
        assert final_stats["active_requests"] == 0
        assert final_stats["max_concurrent_requests"] == 2
        assert final_stats["total_requests"] == 2
    
    def test_memory_tracking(self):
        """Test memory usage tracking."""
        monitor = PerformanceMonitor()
        
        with monitor.track_operation("memory_test"):
            # Allocate some memory
            data = [0] * 1000000
        
        memory_stats = monitor.get_memory_stats()
        assert memory_stats["current_memory_mb"] > 0
        assert "avg_memory_delta_mb" in memory_stats
    
    def test_operation_stats_filtering(self):
        """Test operation statistics filtering."""
        monitor = PerformanceMonitor()
        
        with monitor.track_operation("operation_a"):
            pass
        
        with monitor.track_operation("operation_b"):
            pass
        
        stats_a = monitor.get_operation_stats("operation_a")
        stats_b = monitor.get_operation_stats("operation_b")
        stats_all = monitor.get_operation_stats()
        
        assert stats_a["count"] == 1
        assert stats_b["count"] == 1
        assert stats_all["count"] == 2
    
    def test_performance_threshold_check(self):
        """Test performance threshold checking."""
        monitor = PerformanceMonitor()
        
        with monitor.track_operation("fast_operation"):
            time.sleep(0.01)
        
        # Should pass threshold
        assert monitor.check_performance_threshold("fast_operation", 1.0) is True
        
        # Should fail threshold
        assert monitor.check_performance_threshold("fast_operation", 0.001) is False
    
    def test_get_summary(self):
        """Test getting comprehensive summary."""
        monitor = PerformanceMonitor()
        
        with monitor.track_operation("test_op"):
            pass
        
        summary = monitor.get_summary()
        
        assert "operation_stats" in summary
        assert "memory_stats" in summary
        assert "concurrent_request_stats" in summary
        assert "recent_operations" in summary
    
    def test_reset_stats(self):
        """Test resetting statistics."""
        monitor = PerformanceMonitor()
        
        with monitor.track_operation("test_operation"):
            pass
        
        assert monitor.get_operation_stats()["count"] == 1
        
        monitor.reset_stats()
        
        assert monitor.get_operation_stats()["count"] == 0
        assert monitor.get_concurrent_request_stats()["total_requests"] == 0
    
    def test_global_monitor_singleton(self):
        """Test global monitor singleton pattern."""
        monitor1 = get_performance_monitor()
        monitor2 = get_performance_monitor()
        
        assert monitor1 is monitor2
    
    def test_max_history_limit(self):
        """Test that history respects max limit."""
        monitor = PerformanceMonitor(max_history=5)
        
        # Add more operations than max_history
        for i in range(10):
            with monitor.track_operation(f"operation_{i}"):
                pass
        
        # Should only keep last 5
        recent = monitor.get_recent_operations(limit=100)
        assert len(recent) <= 5
