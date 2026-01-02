# Performance Monitoring Implementation

## Overview

The Legal Case Similarity application includes comprehensive performance monitoring to track response times, manage concurrent requests, and monitor memory usage.

## Features

### 1. Response Time Tracking (Requirement 5.1)

The `PerformanceMonitor` class tracks the duration of all operations:

- **Upload and search operations**: Full end-to-end timing
- **PDF extraction**: Time to extract text from PDFs
- **Text preprocessing**: Time to clean and normalize text
- **Vectorization**: Time to convert text to TF-IDF vectors
- **Similarity search**: Time to find similar cases

### 2. Concurrent Request Handling (Requirement 5.2)

The monitor tracks concurrent request metrics:

- **Active requests**: Current number of requests being processed
- **Max concurrent requests**: Peak concurrent request count
- **Total requests**: Cumulative request count

### 3. Memory Usage Monitoring (Requirement 5.3)

Memory tracking for large document processing:

- **Current memory usage**: Real-time memory consumption in MB
- **Memory delta per operation**: Memory change during each operation
- **Average/min/max memory deltas**: Statistical memory usage patterns

## Usage

### In Application Code

```python
from src.components.performance_monitor import get_performance_monitor

monitor = get_performance_monitor()

# Track an operation
with monitor.track_operation("my_operation", metadata={"key": "value"}):
    # Perform operation
    pass
```

### API Endpoints

#### Get Performance Metrics

```bash
GET /api/performance
```

Returns detailed performance statistics including:
- Operation statistics (count, avg/min/max duration, success rate)
- Memory statistics (current usage, deltas)
- Concurrent request statistics
- Recent operations

#### Health Check with Performance

```bash
GET /api/health
```

Returns system health including performance metrics:
- Concurrent request stats
- Search performance stats
- Upload performance stats

## Implementation Details

### PerformanceMonitor Class

Located in `src/components/performance_monitor.py`:

- **Thread-safe**: Uses locks for concurrent access
- **Context manager**: Easy integration with `with` statements
- **Configurable history**: Maintains last N operations (default: 1000)
- **Automatic cleanup**: Removes completed operations from active tracking

### Integration Points

1. **API Upload Endpoint** (`/api/upload`):
   - Tracks entire upload and search operation
   - Tracks individual sub-operations (extraction, preprocessing, vectorization, search)

2. **Health Endpoint** (`/api/health`):
   - Includes performance metrics in response
   - Shows concurrent request statistics

3. **Performance Endpoint** (`/api/performance`):
   - Dedicated endpoint for detailed metrics
   - Useful for monitoring and debugging

## Performance Thresholds

The system includes threshold checking:

```python
# Check if operations meet performance requirements
is_fast_enough = monitor.check_performance_threshold(
    operation_name="similarity_search",
    max_duration=10.0  # 10 seconds (Requirement 5.1)
)
```

## Testing

Comprehensive test coverage in:
- `tests/unit/test_performance_monitor.py`: Unit tests for PerformanceMonitor
- `tests/unit/test_api_performance_integration.py`: Integration tests with API

All tests verify:
- Response time tracking accuracy
- Concurrent request counting
- Memory usage monitoring
- API endpoint integration

## Dependencies

- **psutil**: For memory usage monitoring (added to requirements.txt)

## Future Enhancements

Potential improvements:
- Persistent metrics storage (database or time-series DB)
- Alerting when thresholds are exceeded
- Performance dashboards and visualization
- Distributed tracing for microservices
