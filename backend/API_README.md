# Legal Case Similarity API

A FastAPI-based web service for finding similar legal cases using document similarity analysis.

## Features

- **PDF Upload & Analysis**: Upload PDF documents and find similar legal cases
- **Comprehensive Error Handling**: Standardized error responses with appropriate HTTP status codes
- **Case Management**: Retrieve case details and download original documents
- **Health Monitoring**: System health checks and component status
- **Web Interface**: Built-in web frontend for easy interaction

## API Endpoints

### POST /api/upload
Upload a PDF document and receive similar cases ranked by similarity score.

**Request**: Multipart form data with PDF file
**Response**: JSON with similar cases, processing time, and metadata

### GET /api/cases/{case_id}
Get detailed information about a specific case.

**Response**: JSON with case details including title, date, and metadata

### GET /api/cases/{case_id}/download
Download the original PDF file for a specific case.

**Response**: PDF file as streaming download

### GET /api/health
Get system health status and component information.

**Response**: JSON with system status, component health, and statistics

### GET /api/view
Serve the web frontend interface.

**Response**: HTML page with upload form and results display

## Running the API

### Using the startup script:
```bash
python run_api.py
```

### Using uvicorn directly:
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Environment Variables:
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `RELOAD`: Enable auto-reload (default: true)
- `LOG_LEVEL`: Logging level (default: info)

## Error Handling

The API provides comprehensive error handling with standardized JSON error responses:

```json
{
  "error": true,
  "message": "Descriptive error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### HTTP Status Codes:
- `400`: Bad Request (invalid file format, missing parameters)
- `413`: Payload Too Large (file size exceeds limit)
- `422`: Unprocessable Entity (valid PDF but processing failed)
- `500`: Internal Server Error (system failures)

## Requirements

The API requires the following components to be properly initialized:
- PDF processor for text extraction
- Text preprocessor for normalization
- Legal vectorizer (trained model)
- Case repository with metadata and vectors
- Similarity search engine

## Development

The API is built with:
- **FastAPI**: Modern, fast web framework
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server
- **CORS**: Cross-origin resource sharing support

## Validation

The API includes comprehensive request validation:
- File type validation (PDF only)
- File size limits (10MB maximum)
- Content validation and error handling
- Standardized error responses

## Logging

The API provides detailed logging for:
- Request processing times
- Error conditions and stack traces
- Component initialization status
- System health information