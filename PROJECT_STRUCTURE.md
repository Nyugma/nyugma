# Project Structure

This document describes the reorganized project structure with separated frontend and backend.

## Directory Layout

```
legal-case-similarity/
│
├── frontend/                      # Frontend application (Static files)
│   ├── css/                       # Stylesheets
│   │   ├── home.css              # Home page styles
│   │   └── styles.css            # Search page styles
│   │
│   ├── js/                        # JavaScript modules
│   │   ├── app.js                # Search functionality
│   │   ├── config.js             # Backend URL configuration
│   │   ├── navigation.js         # Navigation handling
│   │   └── env.js.template       # Environment template
│   │
│   ├── index.html                 # Home/landing page
│   ├── search.html                # Search interface
│   ├── .gitignore                 # Frontend-specific ignores
│   ├── README.md                  # Frontend documentation
│   ├── DEPLOYMENT.md              # Frontend deployment guide
│   ├── netlify.toml               # Netlify configuration
│   ├── vercel.json                # Vercel configuration
│   ├── build.sh                   # Build script (Unix)
│   └── build.ps1                  # Build script (Windows)
│
├── backend/                       # Backend application (Python API)
│   ├── src/                       # Source code
│   │   ├── api/                   # API endpoints
│   │   │   ├── main.py           # FastAPI application
│   │   │   └── __init__.py
│   │   │
│   │   ├── components/            # Core processing components
│   │   │   ├── case_repository.py
│   │   │   ├── legal_vectorizer.py
│   │   │   ├── pdf_processor.py
│   │   │   ├── performance_monitor.py
│   │   │   ├── similarity_search_engine.py
│   │   │   ├── text_preprocessor.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── models/                # Data models
│   │   │   ├── case_document.py
│   │   │   ├── legal_vocabulary.py
│   │   │   ├── search_result.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── config/                # Configuration
│   │   │   ├── logging_config.py
│   │   │   ├── settings.py
│   │   │   └── __init__.py
│   │   │
│   │   └── __init__.py
│   │
│   ├── data/                      # Data storage
│   │   ├── cases/                 # PDF case files
│   │   │   ├── .gitkeep
│   │   │   └── case_*.pdf        # Sample cases
│   │   │
│   │   ├── vectors/               # Pre-computed vectors
│   │   │   ├── .gitkeep
│   │   │   └── case_vectors.pkl
│   │   │
│   │   ├── cases_metadata.json    # Case metadata
│   │   ├── legal_vocabulary.json  # Legal terms
│   │   └── vectorizer_model.pkl   # Trained model
│   │
│   ├── tests/                     # Test suite
│   │   ├── unit/                  # Unit tests
│   │   │   ├── test_performance_monitor.py
│   │   │   ├── test_health_check_cors.py
│   │   │   └── test_api_performance_integration.py
│   │   │
│   │   ├── integration/           # Integration tests
│   │   │   ├── test_end_to_end.py
│   │   │   └── test_root_endpoint.py
│   │   │
│   │   ├── property/              # Property-based tests
│   │   └── test_setup.py
│   │
│   ├── logs/                      # Application logs
│   │   ├── .gitkeep
│   │   ├── app.log
│   │   └── error.log
│   │
│   ├── scripts/                   # Utility scripts
│   │   └── generate_sample_data.py
│   │
│   ├── main.py                    # Application entry point
│   ├── run_api.py                 # Development server
│   ├── uvicorn_production.py      # Production server
│   ├── verify_setup.py            # Setup verification
│   ├── requirements.txt           # Python dependencies
│   ├── requirements-dev.txt       # Dev dependencies
│   ├── pytest.ini                 # Pytest configuration
│   ├── Dockerfile                 # Docker configuration
│   ├── docker-compose.yml         # Docker Compose config
│   ├── render.yaml                # Render deployment config
│   ├── .dockerignore              # Docker ignore rules
│   ├── .env.example               # Environment template
│   ├── .gitignore                 # Backend-specific ignores
│   ├── README.md                  # Backend documentation
│   ├── API_README.md              # API documentation
│   └── DEPLOYMENT.md              # Backend deployment guide
│
├── .git/                          # Git repository
├── .venv/                         # Python virtual environment
│
├── .gitignore                     # Root-level ignores
├── README.md                      # Project overview
├── DEPLOYMENT_GUIDE.md            # Complete deployment guide
└── PROJECT_STRUCTURE.md           # This file
```

## Key Changes from Original Structure

### Before (Monolithic)
```
legal-case-similarity/
├── src/                  # Backend code
├── frontend/             # Frontend code
├── static/               # Duplicate static files
├── templates/            # Server-side templates
├── data/                 # Data files
├── tests/                # Tests
├── main.py               # Entry point
└── requirements.txt      # Dependencies
```

### After (Separated)
```
legal-case-similarity/
├── frontend/             # Complete frontend app
│   ├── css/
│   ├── js/
│   ├── *.html
│   └── README.md
│
└── backend/              # Complete backend app
    ├── src/
    ├── data/
    ├── tests/
    ├── main.py
    ├── requirements.txt
    └── README.md
```

## Benefits of New Structure

### 1. Independent Deployment
- Deploy frontend and backend separately
- Use different hosting platforms optimized for each
- Scale components independently

### 2. Clear Separation of Concerns
- Frontend: Pure static files (HTML/CSS/JS)
- Backend: Pure API (JSON responses only)
- No mixing of server-side templates with API

### 3. Easier Development
- Work on frontend without running backend
- Work on backend without frontend
- Clear boundaries between components

### 4. Better Version Control
- Changes to frontend don't affect backend
- Changes to backend don't affect frontend
- Easier to track changes per component

### 5. Flexible Hosting
- **Frontend**: Netlify, Vercel, GitHub Pages, S3, etc.
- **Backend**: Render, Heroku, Railway, AWS, GCP, etc.
- Choose best platform for each component

## Deployment Targets

### Frontend (Static Hosting)
- **Netlify** ✅ Recommended
  - Automatic deployments
  - Free SSL
  - CDN included
  - Environment variables

- **Vercel** ✅ Recommended
  - Similar to Netlify
  - Excellent performance
  - Easy configuration

- **GitHub Pages**
  - Free for public repos
  - Simple setup
  - Limited configuration

### Backend (Python Hosting)
- **Render** ✅ Recommended
  - Free tier available
  - Easy Python deployment
  - Automatic HTTPS
  - Good documentation

- **Railway**
  - Simple deployment
  - Good free tier
  - Modern interface

- **Heroku**
  - Mature platform
  - Paid plans only
  - Extensive add-ons

- **Docker** (Self-hosted)
  - Full control
  - Any cloud provider
  - Requires more setup

## File Organization Principles

### Frontend Files
- **HTML**: Page structure and content
- **CSS**: Styling and responsive design
- **JS**: Client-side logic and API calls
- **Config**: Backend URL configuration
- **Docs**: Deployment and usage guides

### Backend Files
- **src/**: All Python source code
- **data/**: Application data and models
- **tests/**: Test suite
- **logs/**: Application logs
- **scripts/**: Utility scripts
- **Config files**: Docker, requirements, etc.
- **Docs**: API and deployment guides

## Environment Configuration

### Frontend
```javascript
// js/config.js
function getBackendUrl() {
  // Development
  if (window.location.hostname === 'localhost') {
    return 'http://localhost:8000';
  }
  // Production
  return window.ENV?.BACKEND_URL || 'https://api.example.com';
}
```

### Backend
```python
# Environment variables
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=https://frontend.example.com
```

## Development Workflow

### 1. Local Development
```bash
# Terminal 1: Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run_api.py

# Terminal 2: Frontend
cd frontend
python -m http.server 3000
```

### 2. Testing
```bash
# Backend tests
cd backend
pytest

# Frontend testing
# Open browser to http://localhost:3000
```

### 3. Deployment
```bash
# Deploy backend first
# Note the backend URL

# Deploy frontend
# Configure backend URL in environment variables
```

## Migration Notes

### Removed Files/Folders
- `static/` - Merged into `frontend/`
- `templates/` - No longer needed (API-only backend)
- Root-level config files - Moved to `backend/`

### Consolidated Files
- All backend code → `backend/`
- All frontend code → `frontend/`
- Documentation split between both

### New Files
- `frontend/.gitignore` - Frontend-specific ignores
- `backend/.gitignore` - Backend-specific ignores
- `DEPLOYMENT_GUIDE.md` - Complete deployment instructions
- `PROJECT_STRUCTURE.md` - This file

## Next Steps

1. **Review Documentation**
   - Read `README.md` for project overview
   - Read `frontend/README.md` for frontend details
   - Read `backend/README.md` for backend details

2. **Local Testing**
   - Start backend: `cd backend && python run_api.py`
   - Start frontend: `cd frontend && python -m http.server 3000`
   - Test in browser: `http://localhost:3000`

3. **Deploy**
   - Follow `DEPLOYMENT_GUIDE.md`
   - Deploy backend first
   - Then deploy frontend with backend URL

4. **Configure**
   - Set CORS on backend
   - Set backend URL on frontend
   - Test end-to-end

## Support

For questions or issues:
- Check component-specific README files
- Review DEPLOYMENT_GUIDE.md
- Check API documentation in backend/API_README.md
