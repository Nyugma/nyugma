"""
FastAPI application for Legal Case Similarity Web Application

This module provides the main FastAPI application with endpoints for:
- PDF file upload and similarity search
- Case retrieval and metadata access
- System health monitoring
"""

import os
import tempfile
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, status, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError
import traceback

from src.components.pdf_processor import PDFProcessor
from src.components.text_preprocessor import TextPreprocessor
from src.components.legal_vectorizer import LegalVectorizer
from src.components.similarity_search_engine import SimilaritySearchEngine
from src.components.case_repository import CaseRepository
from src.components.performance_monitor import get_performance_monitor
from src.models.legal_vocabulary import LegalVocabulary
from src.models.search_result import SearchResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Legal Case Similarity API",
    description="API for finding similar legal cases using document similarity analysis",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
pdf_processor = PDFProcessor()
text_preprocessor = TextPreprocessor(enable_lemmatization=True)
case_repository = CaseRepository()
performance_monitor = get_performance_monitor()

# Initialize vectorizer with legal vocabulary
legal_vocabulary = LegalVocabulary()
vectorizer = LegalVectorizer(vocabulary=legal_vocabulary)

# Load pre-trained vectorizer model if available
vectorizer_model_path = Path("data/vectorizer_model.pkl")
if vectorizer_model_path.exists():
    try:
        vectorizer.load_model(vectorizer_model_path)
        logger.info("Loaded pre-trained vectorizer model")
    except Exception as e:
        logger.warning(f"Failed to load vectorizer model: {e}")

# Initialize similarity search engine
case_vectors = case_repository.load_case_vectors()
case_metadata = case_repository.load_case_metadata()

if case_vectors is not None and case_metadata:
    similarity_engine = SimilaritySearchEngine(case_vectors, case_metadata)
    logger.info(f"Initialized similarity engine with {len(case_metadata)} cases")
else:
    similarity_engine = None
    logger.warning("No case data available - similarity search will be limited")


# Pydantic models for request/response validation
class SimilarCase(BaseModel):
    """Model for similar case in search results."""
    case_id: str = Field(..., description="Unique case identifier")
    title: str = Field(..., description="Case title")
    date: str = Field(..., description="Case date")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score (0-1)")
    snippet: str = Field(..., description="Brief text excerpt")
    download_url: str = Field(..., description="URL to download case file")


class UploadResponse(BaseModel):
    """Response model for file upload endpoint."""
    results: List[SimilarCase] = Field(..., description="List of similar cases")
    processing_time: float = Field(..., description="Processing time in seconds")
    query_id: str = Field(..., description="Unique query identifier")
    total_cases_searched: int = Field(..., description="Total number of cases in repository")


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: bool = Field(True, description="Error flag")
    message: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    timestamp: str = Field(..., description="Error timestamp")


# Configuration constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_CONTENT_TYPES = ["application/pdf"]
DEFAULT_RESULTS_COUNT = 10


# Utility functions for error handling
def create_error_response(
    message: str,
    error_code: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
) -> HTTPException:
    """
    Create a standardized HTTPException with error response format.
    
    Args:
        message: Error message
        error_code: Error code identifier
        status_code: HTTP status code
        
    Returns:
        HTTPException with standardized error detail
        
    Requirements: 7.3, 7.4, 7.5 - Standardized error responses
    """
    error_detail = {
        "error": True,
        "message": message,
        "error_code": error_code,
        "timestamp": datetime.now().isoformat()
    }
    
    return HTTPException(status_code=status_code, detail=error_detail)


def validate_file_upload(file: UploadFile) -> None:
    """
    Validate uploaded file meets requirements.
    
    Args:
        file: Uploaded file to validate
        
    Raises:
        HTTPException: If file validation fails
        
    Requirements: 7.4 - Request validation
    """
    # Validate file size
    if file.size and file.size > MAX_FILE_SIZE:
        raise create_error_response(
            message=f"File size ({file.size} bytes) exceeds maximum allowed size ({MAX_FILE_SIZE} bytes)",
            error_code="FILE_TOO_LARGE",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        )
    
    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise create_error_response(
            message=f"Invalid file type: {file.content_type}. Only PDF files are allowed.",
            error_code="INVALID_FILE_TYPE",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate filename
    if not file.filename:
        raise create_error_response(
            message="Filename is required",
            error_code="MISSING_FILENAME",
            status_code=status.HTTP_400_BAD_REQUEST
        )


# Global error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions with standardized error response format.
    
    Requirements: 7.3, 7.4, 7.5 - Error handling and response formatting
    """
    # If detail is already a dict (from our custom HTTPExceptions), use it directly
    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )
    
    # Otherwise, create standardized error response
    error_response = {
        "error": True,
        "message": str(exc.detail),
        "error_code": f"HTTP_{exc.status_code}",
        "timestamp": datetime.now().isoformat()
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors with detailed error information.
    
    Requirements: 7.4 - Request validation error handling
    """
    error_details = []
    for error in exc.errors():
        error_details.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    error_response = {
        "error": True,
        "message": "Request validation failed",
        "error_code": "VALIDATION_ERROR",
        "timestamp": datetime.now().isoformat(),
        "details": error_details
    }
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """
    Handle Pydantic model validation errors.
    
    Requirements: 7.4 - Data validation error handling
    """
    error_response = {
        "error": True,
        "message": "Data validation failed",
        "error_code": "MODEL_VALIDATION_ERROR",
        "timestamp": datetime.now().isoformat(),
        "details": exc.errors()
    }
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all other unexpected exceptions with generic error response.
    
    Requirements: 7.5 - General error handling
    """
    logger.error(f"Unexpected error: {exc}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    error_response = {
        "error": True,
        "message": "An internal server error occurred",
        "error_code": "INTERNAL_SERVER_ERROR",
        "timestamp": datetime.now().isoformat()
    }
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response
    )


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to frontend interface."""
    return HTMLResponse("""
    <html>
        <head>
            <meta http-equiv="refresh" content="0; url=/api/view">
        </head>
        <body>
            <p>Redirecting to <a href="/api/view">Legal Case Similarity Search</a>...</p>
        </body>
    </html>
    """)


@app.post(
    "/api/upload",
    response_model=UploadResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request - Invalid file format"},
        413: {"model": ErrorResponse, "description": "Payload Too Large - File size exceeds limit"},
        422: {"model": ErrorResponse, "description": "Unprocessable Entity - PDF processing failed"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Upload PDF and find similar cases",
    description="Upload a PDF document and receive a list of similar legal cases ranked by similarity score"
)
async def upload_pdf(
    file: UploadFile = File(..., description="PDF file to analyze")
) -> UploadResponse:
    """
    Upload a PDF file and find similar legal cases.
    
    This endpoint:
    1. Validates the uploaded file is a PDF
    2. Extracts text content from the PDF
    3. Preprocesses the text for analysis
    4. Converts text to TF-IDF vector
    5. Searches for similar cases using cosine similarity
    6. Returns ranked list of similar cases
    
    Requirements: 7.1 - Upload endpoint functionality
    """
    start_time = datetime.now()
    query_id = f"query_{int(start_time.timestamp())}"
    
    # Track the entire upload operation
    with performance_monitor.track_operation(
        "upload_and_search",
        metadata={"query_id": query_id, "filename": file.filename}
    ):
        try:
            # Validate file upload
            validate_file_upload(file)
            
            # Read file content
            file_content = await file.read()
            
            # Validate PDF format using PDFProcessor
            if not pdf_processor.validate_pdf(file_content):
                raise create_error_response(
                    message="Invalid PDF file format or corrupted file",
                    error_code="INVALID_PDF_FORMAT",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Extract text from PDF with performance tracking
            with performance_monitor.track_operation("pdf_extraction"):
                try:
                    extracted_text = pdf_processor.extract_text_from_bytes(file_content, file.filename or "uploaded.pdf")
                except ValueError as e:
                    raise create_error_response(
                        message=f"Failed to extract text from PDF: {str(e)}",
                        error_code="PDF_EXTRACTION_FAILED",
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
                    )
            
            # Preprocess text with performance tracking
            with performance_monitor.track_operation("text_preprocessing"):
                try:
                    processed_text = text_preprocessor.preprocess(extracted_text)
                    if not processed_text.strip():
                        raise create_error_response(
                            message="No meaningful text content found in PDF after preprocessing",
                            error_code="NO_TEXT_CONTENT",
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
                        )
                except Exception as e:
                    raise create_error_response(
                        message=f"Text preprocessing failed: {str(e)}",
                        error_code="PREPROCESSING_FAILED",
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            # Check if vectorizer is available and fitted
            if not vectorizer.is_fitted:
                raise create_error_response(
                    message="Vectorizer model is not available. Please contact system administrator.",
                    error_code="VECTORIZER_NOT_READY",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Convert text to vector with performance tracking
            with performance_monitor.track_operation("vectorization"):
                try:
                    query_vector = vectorizer.transform([processed_text])[0]
                except Exception as e:
                    raise create_error_response(
                        message=f"Text vectorization failed: {str(e)}",
                        error_code="VECTORIZATION_FAILED",
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            # Check if similarity engine is available
            if similarity_engine is None:
                raise create_error_response(
                    message="No case repository available for similarity search",
                    error_code="NO_CASE_REPOSITORY",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Perform similarity search with performance tracking
            with performance_monitor.track_operation(
                "similarity_search",
                metadata={"case_count": similarity_engine.get_case_count()}
            ):
                try:
                    search_results = similarity_engine.search(query_vector, k=DEFAULT_RESULTS_COUNT)
                except Exception as e:
                    raise create_error_response(
                        message=f"Similarity search failed: {str(e)}",
                        error_code="SEARCH_FAILED",
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            # Convert search results to response format
            similar_cases = []
            for result in search_results:
                similar_case = SimilarCase(
                    case_id=result.case_id,
                    title=result.title,
                    date=result.date,
                    similarity_score=result.similarity_score,
                    snippet=result.snippet,
                    download_url=f"/api/cases/{result.case_id}/download"
                )
                similar_cases.append(similar_case)
            
            # Calculate processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Create response
            response = UploadResponse(
                results=similar_cases,
                processing_time=processing_time,
                query_id=query_id,
                total_cases_searched=similarity_engine.get_case_count()
            )
            
            logger.info(f"Successfully processed upload {query_id} in {processing_time:.2f}s, found {len(similar_cases)} results")
            return response
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            # Handle any unexpected errors
            logger.error(f"Unexpected error in upload endpoint: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise create_error_response(
                message="An unexpected error occurred during processing",
                error_code="INTERNAL_ERROR",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Additional Pydantic models for new endpoints
class CaseDetail(BaseModel):
    """Model for detailed case information."""
    case_id: str = Field(..., description="Unique case identifier")
    title: str = Field(..., description="Case title")
    date: str = Field(..., description="Case date")
    file_path: str = Field(..., description="Path to case file")
    metadata: dict = Field(default_factory=dict, description="Additional case metadata")
    download_url: str = Field(..., description="URL to download case file")


class HealthStatus(BaseModel):
    """Model for system health status."""
    status: str = Field(..., description="System status")
    timestamp: str = Field(..., description="Status check timestamp")
    version: str = Field(..., description="API version")
    components: dict = Field(..., description="Component status information")
    statistics: dict = Field(..., description="System statistics")
    performance: dict = Field(default_factory=dict, description="Performance metrics")


class PerformanceStats(BaseModel):
    """Model for performance statistics."""
    operation_stats: dict = Field(..., description="Operation statistics")
    memory_stats: dict = Field(..., description="Memory usage statistics")
    concurrent_request_stats: dict = Field(..., description="Concurrent request statistics")
    recent_operations: List[dict] = Field(..., description="Recent operations")


@app.get(
    "/api/cases/{case_id}",
    response_model=CaseDetail,
    responses={
        404: {"model": ErrorResponse, "description": "Case not found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Get case details by ID",
    description="Retrieve detailed information about a specific legal case by its unique identifier"
)
async def get_case_details(case_id: str) -> CaseDetail:
    """
    Get detailed information about a specific case.
    
    Args:
        case_id: Unique identifier for the case
        
    Returns:
        Detailed case information including metadata and download URL
        
    Requirements: 7.2 - Case details endpoint
    """
    try:
        # Retrieve case from repository
        case_document = case_repository.get_case_by_id(case_id)
        
        if case_document is None:
            raise create_error_response(
                message=f"Case with ID '{case_id}' not found",
                error_code="CASE_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Create response model
        case_detail = CaseDetail(
            case_id=case_document.case_id,
            title=case_document.title,
            date=case_document.date.isoformat(),
            file_path=case_document.file_path,
            metadata=case_document.metadata or {},
            download_url=f"/api/cases/{case_id}/download"
        )
        
        return case_detail
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving case {case_id}: {e}")
        raise create_error_response(
            message=f"Failed to retrieve case details: {str(e)}",
            error_code="CASE_RETRIEVAL_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@app.get(
    "/api/cases/{case_id}/download",
    responses={
        200: {"description": "Case file download", "content": {"application/pdf": {}}},
        404: {"model": ErrorResponse, "description": "Case not found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Download case file",
    description="Download the original PDF file for a specific legal case"
)
async def download_case_file(case_id: str):
    """
    Download the original PDF file for a case.
    
    Args:
        case_id: Unique identifier for the case
        
    Returns:
        PDF file as streaming response
        
    Requirements: 7.2 - Case file download
    """
    try:
        # Retrieve case from repository
        case_document = case_repository.get_case_by_id(case_id)
        
        if case_document is None:
            raise create_error_response(
                message=f"Case with ID '{case_id}' not found",
                error_code="CASE_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Check if file exists
        file_path = Path(case_document.file_path)
        if not file_path.exists():
            raise create_error_response(
                message=f"Case file not found on disk: {case_document.file_path}",
                error_code="FILE_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Return file as streaming response
        return FileResponse(
            path=str(file_path),
            media_type="application/pdf",
            filename=f"{case_id}.pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading case file {case_id}: {e}")
        raise create_error_response(
            message=f"Failed to download case file: {str(e)}",
            error_code="FILE_DOWNLOAD_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@app.get(
    "/api/health",
    response_model=HealthStatus,
    summary="System health check",
    description="Get system health status and component information"
)
async def health_check() -> HealthStatus:
    """
    Get system health status and statistics.
    
    Returns:
        System health information including component status and statistics
        
    Requirements: 7.2 - Health monitoring endpoint
    """
    try:
        # Check component status
        components = {
            "pdf_processor": "healthy",
            "text_preprocessor": "healthy",
            "vectorizer": "healthy" if vectorizer.is_fitted else "not_ready",
            "case_repository": "healthy",
            "similarity_engine": "healthy" if similarity_engine is not None else "not_available"
        }
        
        # Get repository statistics
        case_count = case_repository.get_case_count()
        repository_validation = case_repository.validate_repository()
        
        statistics = {
            "total_cases": case_count,
            "repository_consistent": repository_validation.get("consistent", False),
            "vectorizer_fitted": vectorizer.is_fitted,
            "vector_dimensions": vectorizer.get_vector_dimension() if vectorizer.is_fitted else 0,
            "vocabulary_size": vectorizer.vocabulary_size,
            "max_repository_capacity": case_repository.MAX_REPOSITORY_SIZE
        }
        
        # Get performance metrics
        performance = {
            "concurrent_requests": performance_monitor.get_concurrent_request_stats(),
            "search_performance": performance_monitor.get_operation_stats("similarity_search"),
            "upload_performance": performance_monitor.get_operation_stats("upload_and_search")
        }
        
        # Determine overall system status
        overall_status = "healthy"
        if not vectorizer.is_fitted:
            overall_status = "degraded"
        elif similarity_engine is None:
            overall_status = "degraded"
        elif not repository_validation.get("consistent", False):
            overall_status = "degraded"
        
        health_status = HealthStatus(
            status=overall_status,
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            components=components,
            statistics=statistics,
            performance=performance
        )
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error during health check: {e}")
        # Return degraded status instead of failing
        return HealthStatus(
            status="error",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            components={"system": "error"},
            statistics={"error": str(e)},
            performance={}
        )


@app.get(
    "/api/view",
    responses={
        200: {"description": "Frontend interface", "content": {"text/html": {}}},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Serve frontend interface",
    description="Serve the web frontend interface for the legal case similarity application"
)
async def serve_frontend():
    """
    Serve the frontend web interface.
    
    Returns:
        HTML page for the web interface
        
    Requirements: 7.2 - Frontend serving endpoint
    """
    try:
        # Serve the HTML template file
        template_path = Path("templates/index.html")
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            return HTMLResponse(content=html_content)
        else:
            # Fallback to basic HTML if template not found
            html_content = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Legal Case Similarity</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
                    .error { color: red; padding: 20px; border: 1px solid red; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="error">
                    <h1>Frontend Template Not Found</h1>
                    <p>The frontend template file is missing. Please ensure templates/index.html exists.</p>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Error serving frontend: {e}")
        raise create_error_response(
            message=f"Failed to serve frontend interface: {str(e)}",
            error_code="FRONTEND_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@app.get(
    "/api/performance",
    response_model=PerformanceStats,
    summary="Get performance metrics",
    description="Get detailed performance metrics including operation stats, memory usage, and concurrent request handling"
)
async def get_performance_metrics() -> PerformanceStats:
    """
    Get detailed performance metrics.
    
    Returns:
        Performance statistics including operation times, memory usage, and concurrency
        
    Requirements: 5.1, 5.2, 5.3 - Performance monitoring
    """
    try:
        summary = performance_monitor.get_summary()
        
        return PerformanceStats(
            operation_stats=summary["operation_stats"],
            memory_stats=summary["memory_stats"],
            concurrent_request_stats=summary["concurrent_request_stats"],
            recent_operations=summary["recent_operations"]
        )
        
    except Exception as e:
        logger.error(f"Error retrieving performance metrics: {e}")
        raise create_error_response(
            message=f"Failed to retrieve performance metrics: {str(e)}",
            error_code="PERFORMANCE_METRICS_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)