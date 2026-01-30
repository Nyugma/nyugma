# System Architecture
# System Architecture

## Overview

The Legal Case Similarity Application is a distributed web application that uses Natural Language Processing (NLP) to help legal professionals identify similar historical cases by analyzing uploaded PDF documents. The system follows a modern client-server architecture with clear separation between frontend and backend components.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Frontend (Static Web App)                    │  │
│  │  - HTML/CSS/JavaScript                                    │  │
│  │  - File Upload Interface                                  │  │
│  │  - Results Visualization                                  │  │
│  │  - Responsive UI                                          │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS/JSON
                              │ REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend API Server                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Application                    │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │              API Layer (Endpoints)                  │  │  │
│  │  │  - Upload Handler                                   │  │  │
│  │  │  - Health Check                                     │  │  │
│  │  │  - Case Retrieval                                   │  │  │
│  │  │  - Performance Metrics                              │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │           Processing Components Layer               │  │  │
│  │  │  ┌──────────────┐  ┌──────────────┐                │  │  │
│  │  │  │ PDF          │  │ Text         │                │  │  │
│  │  │  │ Processor    │→ │ Preprocessor │                │  │  │
│  │  │  └──────────────┘  └──────────────┘                │  │  │
│  │  │         │                  │                        │  │  │
│  │  │         ▼                  ▼                        │  │  │
│  │  │  ┌──────────────┐  ┌──────────────┐                │  │  │
│  │  │  │ Legal        │  │ Similarity   │                │  │  │
│  │  │  │ Vectorizer   │→ │ Search       │                │  │  │
│  │  │  └──────────────┘  └──────────────┘                │  │  │
│  │  │         │                  │                        │  │  │
│  │  │         ▼                  ▼                        │  │  │
│  │  │  ┌──────────────────────────────┐                  │  │  │
│  │  │  │    Case Repository           │                  │  │  │
│  │  │  └──────────────────────────────┘                  │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Data Layer                             │  │
│  │  - PDF Files (cases/)                                     │  │
│  │  - Vector Cache (vectors/)                                │  │
│  │  - Metadata (JSON)                                        │  │
│  │  - TF-IDF Model (PKL)                                     │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Architecture Principles

### 1. Separation of Concerns
- **Frontend**: Pure presentation layer with no business logic
- **Backend**: Pure API with no presentation concerns
- **Data**: Isolated storage layer with clear interfaces

### 2. Independent Deployment
- Frontend and backend can be deployed separately
- Different hosting platforms optimized for each component
- Independent scaling and versioning

### 3. Stateless API
- No session management required
- Each request is self-contained
- Enables horizontal scaling

### 4. RESTful Design
- Standard HTTP methods (GET, POST)
- JSON request/response format
- Clear resource-based URLs

## Component Architecture

### Frontend Architecture

```
frontend/
├── Presentation Layer
│   ├── index.html          # Landing page
│   └── search.html         # Search interface
│
├── Styling Layer
│   └── css/
│       ├── home.css        # Home page styles
│       └── styles.css      # Search page styles
│
└── Logic Layer
    └── js/
        ├── config.js       # Configuration management
        ├── app.js          # Core application logic
        └── navigation.js   # Navigation handling
```

#### Frontend Components

**Configuration Module** (`config.js`)
- Environment detection (development vs production)
- Backend URL resolution
- Runtime configuration

**Application Module** (`app.js`)
- File upload handling
- API communication
- Results rendering
- Error handling
- Progress tracking

**Navigation Module** (`navigation.js`)
- Page routing
- Active state management
- URL handling

### Backend Architecture

```
backend/src/
├── API Layer (api/)
│   └── main.py                    # FastAPI app, routes, middleware
│
├── Components Layer (components/)
│   ├── pdf_processor.py           # PDF text extraction
│   ├── text_preprocessor.py       # Text normalization
│   ├── legal_vectorizer.py        # TF-IDF vectorization
│   ├── similarity_search_engine.py # Cosine similarity search
│   ├── case_repository.py         # Data access layer
│   └── performance_monitor.py     # Metrics collection
│
├── Models Layer (models/)
│   ├── case_document.py           # Case data structure
│   ├── search_result.py           # Search result structure
│   └── legal_vocabulary.py        # Legal terms structure
│
└── Configuration Layer (config/)
    ├── settings.py                # Application settings
    └── logging_config.py          # Logging configuration
```

#### Backend Components

**API Layer**
- Request validation
- Response formatting
- CORS handling
- Error handling
- Middleware (logging, performance)

**PDF Processor**
- Text extraction from PDF files
- Metadata extraction
- Error handling for corrupted files

**Text Preprocessor**
- Tokenization
- Stopword removal
- Lemmatization
- Case normalization
- Special character handling

**Legal Vectorizer**
- TF-IDF model training
- Document vectorization
- Legal vocabulary management
- Model persistence

**Similarity Search Engine**
- Cosine similarity calculation
- Result ranking
- Score normalization
- Efficient vector operations

**Case Repository**
- File system operations
- Metadata management
- Vector caching
- Data persistence

**Performance Monitor**
- Response time tracking
- Request counting
- System metrics
- Performance reporting

## Data Flow

### Upload and Search Flow

```
1. User uploads PDF
   │
   ▼
2. Frontend validates file
   │
   ▼
3. POST /api/upload (multipart/form-data)
   │
   ▼
4. Backend receives file
   │
   ├─► PDF Processor extracts text
   │   │
   │   ▼
   ├─► Text Preprocessor normalizes text
   │   │
   │   ▼
   ├─► Legal Vectorizer creates TF-IDF vector
   │   │
   │   ▼
   ├─► Similarity Search Engine compares with existing cases
   │   │
   │   ▼
   └─► Case Repository retrieves similar case details
       │
       ▼
5. Backend returns JSON response
   │
   ▼
6. Frontend displays results
```

### Detailed Processing Pipeline

```
┌──────────────┐
│ PDF Document │
└──────┬───────┘
       │
       ▼
┌──────────────────────────┐
│ PDF Processor            │
│ - Extract text           │
│ - Extract metadata       │
│ - Handle errors          │
└──────┬───────────────────┘
       │ Raw Text
       ▼
┌──────────────────────────┐
│ Text Preprocessor        │
│ - Tokenize               │
│ - Remove stopwords       │
│ - Lemmatize              │
│ - Normalize case         │
└──────┬───────────────────┘
       │ Processed Tokens
       ▼
┌──────────────────────────┐
│ Legal Vectorizer         │
│ - Apply TF-IDF           │
│ - Weight legal terms     │
│ - Generate vector        │
└──────┬───────────────────┘
       │ Document Vector
       ▼
┌──────────────────────────┐
│ Similarity Search Engine │
│ - Load cached vectors    │
│ - Calculate cosine sim   │
│ - Rank results           │
│ - Filter by threshold    │
└──────┬───────────────────┘
       │ Ranked Results
       ▼
┌──────────────────────────┐
│ Case Repository          │
│ - Fetch case metadata    │
│ - Prepare response       │
└──────┬───────────────────┘
       │
       ▼
┌──────────────┐
│ JSON Response│
└──────────────┘
```

## Technology Stack

### Frontend Technologies

| Technology | Purpose | Rationale |
|------------|---------|-----------|
| HTML5 | Structure | Standard, semantic markup |
| CSS3 | Styling | Modern styling with flexbox/grid |
| Vanilla JavaScript | Logic | No framework overhead, fast loading |
| Fetch API | HTTP requests | Native browser API, promise-based |

### Backend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.8+ | Core language |
| FastAPI | Latest | Web framework |
| Uvicorn | Latest | ASGI server |
| PyMuPDF (fitz) | Latest | PDF processing |
| NLTK | Latest | NLP operations |
| scikit-learn | Latest | ML algorithms |
| Pydantic | Latest | Data validation |

### Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend Hosting | Netlify/Vercel | Static file serving, CDN |
| Backend Hosting | Render/Railway | Python application hosting |
| File Storage | Local filesystem | PDF and vector storage |
| Logging | Python logging | Application monitoring |

## API Design

### RESTful Endpoints

```
GET  /                          # API information
GET  /api/health                # Health check
GET  /api/performance           # Performance metrics
POST /api/upload                # Upload and analyze PDF
GET  /api/cases/{id}            # Get case details
GET  /api/cases/{id}/download   # Download case file
GET  /docs                      # Interactive API docs
```

### Request/Response Format

**Upload Request**
```http
POST /api/upload
Content-Type: multipart/form-data

file: <PDF binary data>
```

**Upload Response**
```json
{
  "message": "File processed successfully",
  "filename": "case_001.pdf",
  "similar_cases": [
    {
      "case_id": "case_002",
      "title": "Smith v. Jones",
      "similarity_score": 0.87,
      "year": 2020,
      "court": "Supreme Court",
      "summary": "Brief case summary..."
    }
  ],
  "processing_time": 1.23
}
```

### Error Handling

```json
{
  "detail": "Error message",
  "status_code": 400,
  "timestamp": "2026-01-23T10:30:00Z"
}
```

## Security Architecture

### Frontend Security

- **HTTPS Only**: All production traffic encrypted
- **Input Validation**: File type and size validation
- **XSS Protection**: Content Security Policy headers
- **CORS**: Restricted to known backend origins

### Backend Security

- **CORS Configuration**: Whitelist specific frontend origins
- **File Validation**: PDF format and size limits
- **Input Sanitization**: Validate all user inputs
- **Error Handling**: No sensitive data in error messages
- **Rate Limiting**: Prevent abuse (future enhancement)

### Security Headers

```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: no-referrer
Content-Security-Policy: default-src 'self'
```

## Performance Architecture

### Frontend Performance

- **Static Assets**: Cached by CDN
- **Minimal Dependencies**: No heavy frameworks
- **Lazy Loading**: Load resources as needed
- **Compression**: Gzip/Brotli compression

### Backend Performance

- **Vector Caching**: Pre-computed vectors stored
- **Efficient Algorithms**: Optimized cosine similarity
- **Connection Pooling**: Reuse connections
- **Async Operations**: Non-blocking I/O with FastAPI

### Performance Metrics

```python
{
  "total_requests": 1234,
  "average_response_time": 0.45,
  "p95_response_time": 1.2,
  "p99_response_time": 2.1,
  "error_rate": 0.01
}
```

## Scalability Architecture

### Horizontal Scaling

**Frontend**
- CDN distribution
- Multiple edge locations
- Automatic scaling by hosting platform

**Backend**
- Multiple worker processes
- Load balancer distribution
- Stateless design enables easy scaling

### Vertical Scaling

- Increase worker count
- Increase memory for vector operations
- Faster CPU for text processing

### Future Enhancements

- Database for metadata (PostgreSQL)
- Vector database (Pinecone, Weaviate)
- Caching layer (Redis)
- Message queue (Celery, RabbitMQ)
- Microservices architecture

## Deployment Architecture

### Development Environment

```
┌─────────────────┐         ┌─────────────────┐
│ Frontend        │         │ Backend         │
│ localhost:3000  │◄───────►│ localhost:8000  │
│ Python HTTP     │         │ Uvicorn         │
└─────────────────┘         └─────────────────┘
```

### Production Environment

```
┌──────────────────────────┐
│ CDN (Cloudflare/AWS)     │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐         ┌──────────────────────────┐
│ Frontend                 │         │ Backend                  │
│ Netlify/Vercel           │◄───────►│ Render/Railway           │
│ - Static files           │  HTTPS  │ - FastAPI app            │
│ - SSL/TLS                │         │ - SSL/TLS                │
│ - Global CDN             │         │ - Auto-scaling           │
└──────────────────────────┘         └──────────────────────────┘
```

## Monitoring and Observability

### Logging Architecture

```
Application Logs
├── app.log          # General application logs
└── error.log        # Error-specific logs

Log Levels:
- DEBUG: Detailed diagnostic information
- INFO: General informational messages
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical issues
```

### Metrics Collection

- Request count
- Response times (avg, p95, p99)
- Error rates
- System resources (CPU, memory)
- Cache hit rates

### Health Checks

```
GET /api/health

Response:
{
  "status": "healthy",
  "timestamp": "2026-01-23T10:30:00Z",
  "version": "1.0.0",
  "uptime": 86400
}
```

## Data Architecture

### File System Structure

```
backend/data/
├── cases/                    # PDF storage
│   ├── case_001.pdf
│   ├── case_002.pdf
│   └── ...
│
├── vectors/                  # Vector cache
│   └── case_vectors.pkl
│
├── cases_metadata.json       # Case metadata
├── legal_vocabulary.json     # Legal terms
└── vectorizer_model.pkl      # TF-IDF model
```

### Data Models

**Case Document**
```python
{
  "case_id": "case_001",
  "title": "Smith v. Jones",
  "year": 2020,
  "court": "Supreme Court",
  "summary": "Brief summary...",
  "file_path": "data/cases/case_001.pdf",
  "vector": [0.1, 0.2, ...],  # TF-IDF vector
  "created_at": "2026-01-23T10:30:00Z"
}
```

**Search Result**
```python
{
  "case_id": "case_002",
  "similarity_score": 0.87,
  "case_data": { ... }
}
```

## Configuration Management

### Frontend Configuration

```javascript
// Environment-based configuration
const config = {
  development: {
    backendUrl: 'http://localhost:8000'
  },
  production: {
    backendUrl: process.env.BACKEND_URL
  }
};
```

### Backend Configuration

```python
# Environment variables
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8000))
WORKERS = int(os.getenv('WORKERS', 4))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'info')
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
```

## Testing Architecture

### Frontend Testing

- Manual browser testing
- Cross-browser compatibility
- Responsive design testing
- API integration testing

### Backend Testing

```
tests/
├── unit/                    # Unit tests
│   ├── test_performance_monitor.py
│   ├── test_health_check_cors.py
│   └── test_api_performance_integration.py
│
├── integration/             # Integration tests
│   ├── test_end_to_end.py
│   └── test_root_endpoint.py
│
└── property/                # Property-based tests
```

### Test Coverage

- Unit tests: Component-level testing
- Integration tests: End-to-end workflows
- API tests: Endpoint validation
- Performance tests: Load and stress testing

## Future Architecture Considerations

### Short-term Enhancements

1. **Database Integration**
   - PostgreSQL for metadata
   - Improved query capabilities
   - Better data management

2. **Caching Layer**
   - Redis for frequently accessed data
   - Reduced database load
   - Faster response times

3. **Authentication**
   - User accounts
   - API key management
   - Usage tracking

### Long-term Enhancements

1. **Microservices**
   - Separate PDF processing service
   - Separate vectorization service
   - Independent scaling

2. **Vector Database**
   - Pinecone or Weaviate
   - Faster similarity search
   - Better scalability

3. **Machine Learning Pipeline**
   - Model training service
   - A/B testing framework
   - Continuous improvement

4. **Advanced Features**
   - Real-time collaboration
   - Document annotations
   - Citation network analysis
   - Predictive analytics

## Conclusion

This architecture provides a solid foundation for the Legal Case Similarity Application with clear separation of concerns, independent deployment capabilities, and room for future growth. The stateless, RESTful design enables horizontal scaling, while the modular component structure allows for easy maintenance and enhancement.
