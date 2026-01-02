"""
Performance monitoring component for the Legal Case Similarity application.

This module provides functionality to track response times, manage concurrent requests,
and monitor memory usage for large document processing.

Requirements: 5.1, 5.2, 5.3
"""

import time
import psutil
import threading
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import deque
from dataclasses import dataclass, field
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    memory_before: Optional[float] = None
    memory_after: Optional[float] = None
    memory_delta: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """
    Monitor and track performance metrics for the application.
    
    This class provides:
    - Response time tracking for search operations
    - Concurrent request handling with resource management
    - Memory usage monitoring for large document processing
    """
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize the performance monitor.
        
        Args:
            max_history: Maximum number of metrics to keep in history
        """
        self.max_history = max_history
        self.metrics_history: deque = deque(maxlen=max_history)
        self.active_operations: Dict[str, PerformanceMetrics] = {}
        self.lock = threading.Lock()
        
        # Concurrent request tracking
        self.active_requests = 0
        self.max_concurrent_requests = 0
        self.total_requests = 0
        
        # Process for memory monitoring
        self.process = psutil.Process()
        
        logger.info("PerformanceMonitor initialized")
    
    @contextmanager
    def track_operation(self, operation_name: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Context manager to track an operation's performance.
        
        Usage:
            with monitor.track_operation("search_operation"):
                # perform operation
                pass
        
        Args:
            operation_name: Name of the operation being tracked
            metadata: Optional metadata to attach to the metrics
            
        Yields:
            PerformanceMetrics object that will be populated
            
        Requirements: 5.1 - Response time tracking
        """
        metrics = PerformanceMetrics(
            operation_name=operation_name,
            start_time=time.time(),
            memory_before=self._get_memory_usage(),
            metadata=metadata or {}
        )
        
        operation_id = f"{operation_name}_{id(metrics)}"
        
        with self.lock:
            self.active_operations[operation_id] = metrics
            self.active_requests += 1
            self.total_requests += 1
            if self.active_requests > self.max_concurrent_requests:
                self.max_concurrent_requests = self.active_requests
        
        try:
            yield metrics
            metrics.success = True
        except Exception as e:
            metrics.success = False
            metrics.error_message = str(e)
            logger.error(f"Operation {operation_name} failed: {e}")
            raise
        finally:
            metrics.end_time = time.time()
            metrics.duration = metrics.end_time - metrics.start_time
            metrics.memory_after = self._get_memory_usage()
            metrics.memory_delta = metrics.memory_after - metrics.memory_before
            
            with self.lock:
                self.active_requests -= 1
                self.active_operations.pop(operation_id, None)
                self.metrics_history.append(metrics)
            
            logger.info(
                f"Operation '{operation_name}' completed in {metrics.duration:.3f}s "
                f"(memory delta: {metrics.memory_delta:.2f} MB)"
            )
    
    def _get_memory_usage(self) -> float:
        """
        Get current memory usage in MB.
        
        Returns:
            Memory usage in megabytes
            
        Requirements: 5.3 - Memory usage monitoring
        """
        try:
            memory_info = self.process.memory_info()
            return memory_info.rss / (1024 * 1024)  # Convert bytes to MB
        except Exception as e:
            logger.warning(f"Failed to get memory usage: {e}")
            return 0.0
    
    def get_operation_stats(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for operations.
        
        Args:
            operation_name: Optional filter for specific operation type
            
        Returns:
            Dictionary containing operation statistics
            
        Requirements: 5.1 - Response time tracking
        """
        with self.lock:
            metrics_list = list(self.metrics_history)
        
        if operation_name:
            metrics_list = [m for m in metrics_list if m.operation_name == operation_name]
        
        if not metrics_list:
            return {
                "operation_name": operation_name or "all",
                "count": 0,
                "avg_duration": 0.0,
                "min_duration": 0.0,
                "max_duration": 0.0,
                "success_rate": 0.0
            }
        
        durations = [m.duration for m in metrics_list if m.duration is not None]
        successes = sum(1 for m in metrics_list if m.success)
        
        return {
            "operation_name": operation_name or "all",
            "count": len(metrics_list),
            "avg_duration": sum(durations) / len(durations) if durations else 0.0,
            "min_duration": min(durations) if durations else 0.0,
            "max_duration": max(durations) if durations else 0.0,
            "success_rate": successes / len(metrics_list) if metrics_list else 0.0,
            "total_successes": successes,
            "total_failures": len(metrics_list) - successes
        }
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory usage statistics.
        
        Returns:
            Dictionary containing memory statistics
            
        Requirements: 5.3 - Memory usage monitoring
        """
        with self.lock:
            metrics_list = list(self.metrics_history)
        
        memory_deltas = [
            m.memory_delta for m in metrics_list 
            if m.memory_delta is not None
        ]
        
        current_memory = self._get_memory_usage()
        
        return {
            "current_memory_mb": current_memory,
            "avg_memory_delta_mb": sum(memory_deltas) / len(memory_deltas) if memory_deltas else 0.0,
            "max_memory_delta_mb": max(memory_deltas) if memory_deltas else 0.0,
            "min_memory_delta_mb": min(memory_deltas) if memory_deltas else 0.0,
            "total_operations_tracked": len(memory_deltas)
        }
    
    def get_concurrent_request_stats(self) -> Dict[str, Any]:
        """
        Get concurrent request handling statistics.
        
        Returns:
            Dictionary containing concurrent request statistics
            
        Requirements: 5.2 - Concurrent request handling
        """
        with self.lock:
            return {
                "active_requests": self.active_requests,
                "max_concurrent_requests": self.max_concurrent_requests,
                "total_requests": self.total_requests,
                "active_operations": len(self.active_operations)
            }
    
    def get_recent_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent operations with their metrics.
        
        Args:
            limit: Maximum number of recent operations to return
            
        Returns:
            List of recent operation metrics
        """
        with self.lock:
            recent = list(self.metrics_history)[-limit:]
        
        return [
            {
                "operation_name": m.operation_name,
                "duration": m.duration,
                "memory_delta": m.memory_delta,
                "success": m.success,
                "timestamp": m.start_time,
                "metadata": m.metadata
            }
            for m in recent
        ]
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive performance summary.
        
        Returns:
            Dictionary containing all performance statistics
        """
        return {
            "operation_stats": self.get_operation_stats(),
            "memory_stats": self.get_memory_stats(),
            "concurrent_request_stats": self.get_concurrent_request_stats(),
            "recent_operations": self.get_recent_operations(limit=5)
        }
    
    def check_performance_threshold(
        self, 
        operation_name: str, 
        max_duration: float
    ) -> bool:
        """
        Check if recent operations meet performance threshold.
        
        Args:
            operation_name: Name of operation to check
            max_duration: Maximum acceptable duration in seconds
            
        Returns:
            True if performance is within threshold, False otherwise
            
        Requirements: 5.1 - Response time tracking
        """
        stats = self.get_operation_stats(operation_name)
        
        if stats["count"] == 0:
            return True
        
        return stats["avg_duration"] <= max_duration
    
    def reset_stats(self):
        """Reset all statistics and metrics history."""
        with self.lock:
            self.metrics_history.clear()
            self.active_operations.clear()
            self.active_requests = 0
            self.max_concurrent_requests = 0
            self.total_requests = 0
        
        logger.info("Performance statistics reset")


# Global performance monitor instance
_global_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """
    Get the global performance monitor instance.
    
    Returns:
        Global PerformanceMonitor instance
    """
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor
