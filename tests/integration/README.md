# Integration Tests

## Overview

This directory contains comprehensive end-to-end integration tests for the Legal Case Similarity Web Application.

## Test Suite

**File:** `test_end_to_end.py`  
**Total Tests:** 19  
**Coverage:** All major requirements and functionality

## Running Tests

### Run All Integration Tests
```bash
python -m pytest tests/integration/test_end_to_end.py -v
```

### Run Specific Test Class
```bash
# End-to-end workflow tests
python -m pytest tests/integration/test_end_to_end.py::TestEndToEndWorkflow -v

# Performance tests
python -m pytest tests/integration/test_end_to_end.py::TestPerformanceRequirements -v

# Data integrity tests
python -m pytest tests/integration/test_end_to_end.py::TestDataIntegrity -v

# Error handling tests
python -m pytest tests/integration/test_end_to_end.py::TestErrorHandling -v

# Vectorization tests
python -m pytest tests/integration/test_end_to_end.py::TestVectorizationConsistency -v
```

### Run Specific Test
```bash
python -m pytest tests/integration/test_end_to_end.py::TestEndToEndWorkflow::test_upload_valid_pdf -v
```

### Run with Coverage Report
```bash
python -m pytest tests/integration/test_end_to_end.py --cov=src --cov-report=html
```

## Prerequisites

### 1. Sample Data
The tests require sample legal documents. Generate them using:
```bash
python scripts/generate_sample_data.py 15
```

This creates:
- 15 PDF documents in `data/cases/`
- Metadata file: `data/cases_metadata.json`
- Vector file: `data/vectors/case_vectors.pkl`
- Vectorizer model: `data/vectorizer_model.pkl`

### 2. Dependencies
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Test Categories

### 1. End-to-End Workflow Tests
Tests the complete user workflow from PDF upload to results display.

**Tests:**
- Health endpoint accessibility
- Valid PDF upload and similarity search
- Non-PDF file rejection
- Corrupted PDF handling
- Empty file handling
- Upload without file
- Results ranking order
- Result count limit (top 10)

### 2. Performance Requirements Tests
Validates that the system meets performance requirements.

**Tests:**
- Search response time < 10 seconds (Requirement 5.1)
- Concurrent upload handling (Requirement 5.2)

### 3. Data Integrity Tests
Ensures data consistency and validity.

**Tests:**
- Repository validation
- Case metadata structure
- Vector storage consistency

### 4. Error Handling Tests
Verifies proper error handling for various failure scenarios.

**Tests:**
- Invalid endpoint (404)
- Invalid HTTP method (405)
- Malformed requests
- Large file handling

### 5. Vectorization Consistency Tests
Tests vectorization and text processing consistency.

**Tests:**
- Vectorizer model persistence
- Text preprocessing consistency

## Expected Results

All tests should pass:
```
======================= 19 passed in ~13s =======================
```

## Troubleshooting

### Tests Fail: "Sample data not generated"
**Solution:** Run the sample data generation script:
```bash
python scripts/generate_sample_data.py 15
```

### Tests Fail: "Vectorizer model not found"
**Solution:** The sample data generation script creates the vectorizer model. Run:
```bash
python scripts/generate_sample_data.py 15
```

### Tests Fail: "Module not found"
**Solution:** Ensure you're running from the project root and dependencies are installed:
```bash
pip install -r requirements.txt
python -m pytest tests/integration/test_end_to_end.py -v
```

### Performance Tests Timeout
**Solution:** Performance tests have a 10-second timeout. If your system is slow:
1. Check system resources
2. Reduce the number of sample cases
3. Close other applications

## Test Results

See `INTEGRATION_TEST_RESULTS.md` for detailed test results and requirements coverage.

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Integration Tests
  run: |
    python scripts/generate_sample_data.py 15
    python -m pytest tests/integration/test_end_to_end.py -v
```

## Contributing

When adding new features:
1. Add corresponding integration tests
2. Ensure all existing tests still pass
3. Update this README if needed
4. Document any new test categories

## Contact

For questions about the integration tests, refer to:
- Design document: `.kiro/specs/legal-case-similarity/design.md`
- Requirements: `.kiro/specs/legal-case-similarity/requirements.md`
- Tasks: `.kiro/specs/legal-case-similarity/tasks.md`
