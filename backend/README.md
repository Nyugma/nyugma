# Legal Case Similarity - Backend API

FastAPI backend for the Legal Case Similarity application. This API provides endpoints for uploading legal documents, processing them, and finding similar cases using NLP techniques.

## Features

- **PDF Processing**: Extract text from legal documents using PyMuPDF
- **Text Preprocessing**: Normalize and clean text with NLTK
- **TF-IDF Vectorization**: Convert documents to numerical vectors
- **Cosine Similarity Search**: Find similar cases efficiently
- **RESTful API**: JSON-based API with CORS support
- **Performance Monitoring**: Track response times and system metrics
- **Health Checks**: Monitor API status

## Technology Stack

- **FastAPI** - Modern Python web framework
- **PyMuPDF** - PDF text extraction
- **NLTK** - Natural language processing
- **scikit-learn** - TF-IDF vectorization and similarity
- **Uvicorn** - ASGI server

## Project Structure

```
backend/
├── src/
│   ├── api/              # API endpoints
│   ├── components/       # Core processing components
│   ├── models/           # Data models
│   └── config/           # Configuration files
├── data/                 # Data storage
│   ├── cases/            # PDF case files
│   └── vectors/          # Pre-computed vectors
├── tests/                # Test files
├── logs/                 # Application logs
├── main.py               # FastAPI application entry point
├── run_api.py            # Development server script
├── uvicorn_production.py # Production server script
├── requirements.txt      # Python dependencies
└── Dockerfile            # Docker configuration
```

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download NLTK data**
   ```bash
   python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
   ```

4. **Run the server**
   ```bash
   # Development mode
   python run_api.py
   
   # Production mode
   python uvicorn_production.py
   ```

5. **Test the API**
   ```bash
   curl http://localhost:8000/api/health
   ```

## API Endpoints

- `GET /` - API information
- `GET /api/health` - Health check
- `GET /api/performance` - Performance metrics
- `POST /api/upload` - Upload PDF for similarity analysis
- `GET /api/cases/{case_id}` - Get case details
- `GET /api/cases/{case_id}/download` - Download case file
- `GET /docs` - Interactive API documentation (Swagger UI)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `WORKERS` | `4` | Number of worker processes |
| `LOG_LEVEL` | `info` | Logging level |
| `CORS_ORIGINS` | `*` | Allowed CORS origins (comma-separated) |
| `FRONTEND_URL` | - | Frontend URL for API info |

## Deployment

### Deploy on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure:
   - **Build Command**: `pip install -r requirements.txt && python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"`
   - **Start Command**: `python uvicorn_production.py`
4. Set environment variables:
   ```
   HOST=0.0.0.0
   PORT=8000
   WORKERS=4
   LOG_LEVEL=warning
   CORS_ORIGINS=https://your-frontend-domain.netlify.app
   ```

### Deploy with Docker

```bash
# Build image
docker build -t legal-case-api .

# Run container
docker run -p 8000:8000 \
  -e CORS_ORIGINS=https://your-frontend.com \
  legal-case-api
```

### Deploy with Docker Compose

```bash
docker-compose up -d
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/unit/test_performance_monitor.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/
```

## CORS Configuration

Configure CORS to allow requests from your frontend:

```bash
# Development (allow all)
CORS_ORIGINS=*

# Production (specific domains)
CORS_ORIGINS=https://your-frontend.netlify.app,https://your-frontend.vercel.app
```

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (3.8+)
- Reinstall dependencies: `pip install -r requirements.txt`
- Verify NLTK data is downloaded

### CORS errors
- Ensure `CORS_ORIGINS` includes your frontend URL
- Check that frontend is using correct backend URL

### File upload fails
- Check file size limits
- Verify PDF is valid
- Check logs in `logs/` directory

## License

MIT License
