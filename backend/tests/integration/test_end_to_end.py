"""
End-to-end integration tests for the Legal Case Similarity application.

This module tests the complete workflow from PDF upload to results display,
verifies error handling paths, and validates performance requirements.
"""

import pytest
import sys
import time
import tempfile
import shutil
from pathlib import Path
from io import BytesIO
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.api.main import app
from src.components.case_repository import CaseRepository
from src.components.legal_vectorizer import LegalVectorizer
from src.models.legal_vocabulary import LegalVocabulary


@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture(scope="module")
def sample_pdf_path():
    """Get path to a sample PDF document."""
    return Path("data/cases/case_001.pdf")


@pytest.fixture(scope="module")
def repository():
    """Get the case repository instance."""
    return CaseRepository()


class TestEndToEndWorkflow:
    """Test complete workflow from upload to results display."""
    
    def test_health_endpoint(self, client):
        """Test that the health endpoint is accessible."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_upload_valid_pdf(self, client, sample_pdf_path):
        """Test uploading a valid PDF and receiving similarity results."""
        # Skip if sample data not generated
        if not sample_pdf_path.exists():
            pytest.skip("Sample data not generated. Run scripts/generate_sample_data.py first.")
        
        # Read PDF file
        with open(sample_pdf_path, "rb") as f:
            pdf_content = f.read()
        
        # Upload PDF
        files = {"file": ("test_case.pdf", BytesIO(pdf_content), "application/pdf")}
        response = client.post("/api/upload", files=files)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "results" in data
        assert "processing_time" in data
        assert isinstance(data["results"], list)
        assert isinstance(data["processing_time"], (int, float))
        
        # Check results content
        if len(data["results"]) > 0:
            result = data["results"][0]
            assert "case_id" in result
            assert "title" in result
            assert "similarity_score" in result
            assert "date" in result
            
            # Verify similarity score is in valid range
            assert 0.0 <= result["similarity_score"] <= 1.0
    
    def test_upload_non_pdf_file(self, client):
        """Test that non-PDF files are rejected with appropriate error."""
        # Create a fake text file
        fake_file = BytesIO(b"This is not a PDF file")
        files = {"file": ("test.txt", fake_file, "text/plain")}
        
        response = client.post("/api/upload", files=files)
        
        # Should return error status
        assert response.status_code in [400, 422]
        data = response.json()
        assert "error" in data or "detail" in data
    
    def test_upload_corrupted_pdf(self, client):
        """Test handling of corrupted PDF files."""
        # Create a file with PDF header but invalid content
        corrupted_pdf = b"%PDF-1.4\nThis is corrupted content"
        files = {"file": ("corrupted.pdf", BytesIO(corrupted_pdf), "application/pdf")}
        
        response = client.post("/api/upload", files=files)
        
        # Should return error status
        assert response.status_code in [400, 422, 500]
        data = response.json()
        assert "error" in data or "detail" in data
    
    def test_upload_empty_file(self, client):
        """Test handling of empty file upload."""
        empty_file = BytesIO(b"")
        files = {"file": ("empty.pdf", empty_file, "application/pdf")}
        
        response = client.post("/api/upload", files=files)
        
        # Should return error status
        assert response.status_code in [400, 422]
    
    def test_upload_without_file(self, client):
        """Test upload endpoint without providing a file."""
        response = client.post("/api/upload")
        
        # Should return error status
        assert response.status_code == 422
    
    def test_results_ranking_order(self, client, sample_pdf_path):
        """Test that results are returned in descending order by similarity score."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample data not generated")
        
        with open(sample_pdf_path, "rb") as f:
            pdf_content = f.read()
        
        files = {"file": ("test_case.pdf", BytesIO(pdf_content), "application/pdf")}
        response = client.post("/api/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        # Verify results are sorted by similarity score (descending)
        if len(results) > 1:
            scores = [r["similarity_score"] for r in results]
            assert scores == sorted(scores, reverse=True), "Results should be sorted by similarity score (descending)"
    
    def test_result_count_limit(self, client, sample_pdf_path):
        """Test that results are limited to top 10 matches."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample data not generated")
        
        with open(sample_pdf_path, "rb") as f:
            pdf_content = f.read()
        
        files = {"file": ("test_case.pdf", BytesIO(pdf_content), "application/pdf")}
        response = client.post("/api/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        # Should return at most 10 results
        assert len(results) <= 10, "Should return at most 10 results"


class TestPerformanceRequirements:
    """Test that performance requirements are met."""
    
    def test_search_response_time(self, client, sample_pdf_path):
        """Test that search completes within 10 seconds for up to 1000 documents."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample data not generated")
        
        with open(sample_pdf_path, "rb") as f:
            pdf_content = f.read()
        
        # Measure response time
        start_time = time.time()
        files = {"file": ("test_case.pdf", BytesIO(pdf_content), "application/pdf")}
        response = client.post("/api/upload", files=files)
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        
        assert response.status_code == 200
        # Requirement: search should complete within 10 seconds
        assert elapsed_time < 10.0, f"Search took {elapsed_time:.2f}s, should be < 10s"
        
        # Also check the processing_time in response
        data = response.json()
        assert data["processing_time"] < 10.0
    
    def test_concurrent_uploads(self, client, sample_pdf_path):
        """Test that system handles concurrent uploads without failure."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample data not generated")
        
        with open(sample_pdf_path, "rb") as f:
            pdf_content = f.read()
        
        # Simulate multiple concurrent uploads
        # Note: TestClient doesn't support true concurrency, but we can test sequential requests
        num_requests = 5
        responses = []
        
        for i in range(num_requests):
            files = {"file": (f"test_case_{i}.pdf", BytesIO(pdf_content), "application/pdf")}
            response = client.post("/api/upload", files=files)
            responses.append(response)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert "results" in data


class TestDataIntegrity:
    """Test data integrity and consistency."""
    
    def test_repository_validation(self, repository):
        """Test that repository data is valid and consistent."""
        validation_results = repository.validate_repository()
        
        assert validation_results["consistent"], f"Repository validation failed: {validation_results['issues']}"
        assert validation_results["schema_valid"], "Repository schema is invalid"
        assert validation_results["capacity_ok"], "Repository capacity exceeded"
        
        # Check metadata and vector counts match
        assert validation_results["metadata_count"] == validation_results["vector_count"], \
            "Metadata count doesn't match vector count"
    
    def test_case_metadata_structure(self, repository):
        """Test that all case metadata has required fields."""
        cases_metadata = repository.load_case_metadata()
        
        required_fields = {"case_id", "title", "date", "file_path"}
        
        for case in cases_metadata:
            missing_fields = required_fields - set(case.keys())
            assert not missing_fields, f"Case {case.get('case_id', 'unknown')} missing fields: {missing_fields}"
            
            # Verify field types
            assert isinstance(case["case_id"], str)
            assert isinstance(case["title"], str)
            assert isinstance(case["date"], str)
            assert isinstance(case["file_path"], str)
    
    def test_vector_storage_consistency(self, repository):
        """Test that vectors are stored consistently with metadata."""
        cases_metadata = repository.load_case_metadata()
        vectors = repository.load_case_vectors()
        
        if vectors is not None:
            # Number of vectors should match number of cases
            assert len(vectors) == len(cases_metadata), \
                f"Vector count ({len(vectors)}) doesn't match case count ({len(cases_metadata)})"
            
            # Each case should have a valid vector_index
            for i, case in enumerate(cases_metadata):
                assert case["vector_index"] == i, \
                    f"Case {case['case_id']} has incorrect vector_index"


class TestErrorHandling:
    """Test error handling paths."""
    
    def test_invalid_endpoint(self, client):
        """Test accessing non-existent endpoint."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_http_method(self, client):
        """Test using wrong HTTP method on endpoint."""
        # Upload endpoint expects POST, try GET
        response = client.get("/api/upload")
        assert response.status_code == 405  # Method Not Allowed
    
    def test_malformed_request(self, client):
        """Test handling of malformed requests."""
        # Send invalid data
        response = client.post("/api/upload", data={"invalid": "data"})
        assert response.status_code in [400, 422]
    
    def test_large_file_handling(self, client):
        """Test handling of very large files."""
        # Create a large fake PDF (10MB)
        large_content = b"%PDF-1.4\n" + b"x" * (10 * 1024 * 1024)
        files = {"file": ("large.pdf", BytesIO(large_content), "application/pdf")}
        
        response = client.post("/api/upload", files=files)
        
        # Should either process it or return appropriate error
        assert response.status_code in [200, 413, 422, 500]


class TestVectorizationConsistency:
    """Test vectorization consistency."""
    
    def test_vectorizer_model_persistence(self):
        """Test that vectorizer model can be saved and loaded."""
        model_path = Path("data/vectorizer_model.pkl")
        
        if not model_path.exists():
            pytest.skip("Vectorizer model not found")
        
        # Load the model
        vocabulary = LegalVocabulary()
        vectorizer = LegalVectorizer(vocabulary)
        vectorizer.load_model(model_path)
        
        # Verify it's fitted
        assert vectorizer.is_fitted
        
        # Test transformation
        test_text = "This is a test legal document about custody and property rights."
        vector = vectorizer.transform(test_text)
        
        # Verify vector properties
        assert vector.shape[0] == 1  # One document
        assert vector.shape[1] == vectorizer.vocabulary_size  # Correct dimensions
    
    def test_text_preprocessing_consistency(self):
        """Test that text preprocessing is consistent."""
        from src.components.text_preprocessor import TextPreprocessor
        
        preprocessor = TextPreprocessor()
        
        # Same text should produce same result
        text = "This is a TEST document with PUNCTUATION!!!"
        result1 = preprocessor.preprocess(text)
        result2 = preprocessor.preprocess(text)
        
        assert result1 == result2, "Preprocessing should be deterministic"
        
        # Verify normalization
        assert result1.islower(), "Text should be lowercase"
        assert "!!!" not in result1, "Punctuation should be removed"


def run_integration_tests():
    """Run all integration tests and report results."""
    print("="*60)
    print("Running Integration Tests")
    print("="*60)
    
    # Run pytest with verbose output
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "-s"
    ]
    
    exit_code = pytest.main(pytest_args)
    
    print("\n" + "="*60)
    if exit_code == 0:
        print("✓ All integration tests passed!")
    else:
        print("✗ Some integration tests failed")
    print("="*60)
    
    return exit_code


if __name__ == "__main__":
    exit(run_integration_tests())
