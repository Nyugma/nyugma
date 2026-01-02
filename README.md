# Legal Case Similarity Web Application

A web-based application that helps legal professionals identify similar historical cases by analyzing uploaded PDF documents using Natural Language Processing techniques.

## Project Structure

```
legal-case-similarity/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── pytest.ini            # Pytest configuration
├── README.md              # Project documentation
├── src/                   # Source code
│   ├── __init__.py
│   ├── api/               # API endpoints
│   ├── components/        # Core processing components
│   ├── models/            # Data models
│   └── config/            # Configuration files
│       ├── logging_config.py
│       └── settings.py
├── data/                  # Data storage
│   ├── cases/             # PDF case files
│   └── vectors/           # Pre-computed vectors
├── tests/                 # Test files
│   ├── unit/              # Unit tests
│   └── property/          # Property-based tests
├── static/                # Static web assets
│   ├── css/
│   └── js/
├── templates/             # HTML templates
└── logs/                  # Application logs
```

## Quick Start

### Automated Installation

#### Linux / macOS
```bash
chmod +x install.sh
./install.sh
```

#### Windows
```cmd
install.bat
```

### Manual Installation

1. **Install Python 3.8 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - Ensure Python is added to PATH

2. **Create virtual environment**
   ```bash
   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   
   # Windows
   python -m venv venv
   venv\Scripts\activate.bat
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Download NLTK data**
   ```bash
   python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
   ```

5. **Verify installation**
   ```bash
   python verify_setup.py
   ```

## Running the Application

### Development Mode
```bash
python run_api.py
```

### Production Mode
```bash
python uvicorn_production.py
```

The application will be available at http://localhost:8000

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

## API Endpoints

- `GET /` - Root endpoint (redirects to web interface)
- `GET /api/health` - Health check and system status
- `GET /api/performance` - Performance metrics
- `POST /api/upload` - Upload PDF for similarity analysis
- `GET /api/cases/{case_id}` - Get case details
- `GET /api/cases/{case_id}/download` - Download case file
- `GET /api/view` - Web interface

## Production Deployment

For production deployment, use the production-ready configuration:

```bash
# Direct production mode
python uvicorn_production.py

# Or with custom configuration
export HOST=0.0.0.0
export PORT=8000
export WORKERS=4
export LOG_LEVEL=warning
python uvicorn_production.py
```

### Production Checklist

Before deploying to production, review:
- [DEPLOYMENT.md](DEPLOYMENT.md) - Comprehensive deployment guide
- [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md) - Pre-deployment checklist

### Key Production Considerations

1. **Security**: Update CORS origins in `src/api/main.py`
2. **Performance**: Configure worker count based on CPU cores
3. **Monitoring**: Enable health checks and performance monitoring
4. **Logging**: Configure appropriate log levels and rotation
5. **Backup**: Implement backup strategy for case repository

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on:
- Platform-specific installation (Linux, Windows, macOS)
- Systemd service configuration
- Reverse proxy setup (Nginx, Apache)
- Docker deployment
- Security hardening
- Performance optimization

## Development

Run tests:
```bash
pytest
```

Run with development server:
```bash
uvicorn main:app --reload
```

## Features

- **PDF Processing**: Extract text from legal documents using PyMuPDF
- **Text Preprocessing**: Normalize and clean text with NLTK
- **TF-IDF Vectorization**: Convert documents to numerical vectors with legal vocabulary
- **Cosine Similarity Search**: Find similar cases using efficient similarity algorithms
- **Web Interface**: User-friendly interface for file upload and results display
- **RESTful API**: Programmatic access to all functionality
- **Performance Monitoring**: Track response times and system metrics
- **Cross-Platform**: Runs on Linux, Windows, and macOS

## Cross-Platform Compatibility

This application is designed to run on multiple platforms:

- **Linux**: Ubuntu/Debian, CentOS/RHEL/Fedora
- **Windows**: Windows 10/11, Windows Server
- **macOS**: macOS 10.15+ (Catalina and later)

Platform-specific installation scripts are provided:
- `install.sh` for Linux and macOS
- `install.bat` for Windows

See [DEPLOYMENT.md](DEPLOYMENT.md) for platform-specific instructions and troubleshooting.