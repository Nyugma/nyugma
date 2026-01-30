# Deployment Guide - Legal Case Similarity Web Application

This guide provides comprehensive instructions for deploying the Legal Case Similarity Web Application across different platforms and environments.

**Architecture Note**: This application uses a separated architecture with an independent backend API and frontend. The backend can be deployed on platforms like Render, while the frontend can be deployed on static hosting platforms like Netlify, Vercel, or GitHub Pages.

## Architecture Overview

The application consists of two independently deployable components:

```
┌──────────────────────────┐         ┌──────────────────────────┐
│   Frontend (Static)      │         │   Backend (API Only)     │
│                          │         │                          │
│  - HTML/CSS/JavaScript   │  HTTP   │  - FastAPI Application   │
│  - Configurable API URL  │◄───────►│  - REST API Endpoints    │
│  - Static File Hosting   │ Requests│  - CORS Enabled          │
│                          │         │  - JSON Responses        │
│  Deployed on:            │         │                          │
│  - Netlify               │         │  Deployed on:            │
│  - Vercel                │         │  - Render                │
│  - GitHub Pages          │         │  - Docker                │
│  - Any static host       │         │  - Traditional servers   │
└──────────────────────────┘         └──────────────────────────┘
```

**Key Benefits**:
- Independent scaling of frontend and backend
- Deploy frontend to CDN for global performance
- Backend can be deployed on any Python-compatible platform
- Easy to update either component without affecting the other

## Backend Deployment

The backend is a FastAPI application that provides REST API endpoints for PDF processing and similarity search.

### Render Deployment

Render is a cloud platform that makes it easy to deploy Python applications with automatic HTTPS and continuous deployment.

#### Prerequisites

- GitHub account with your repository
- Render account (free tier available at [render.com](https://render.com))

#### Step 1: Prepare Your Repository

Ensure your repository includes:
- `requirements.txt` with all dependencies
- `uvicorn_production.py` or `run_api.py` for starting the server
- `render.yaml` (optional, for infrastructure as code)

#### Step 2: Create Web Service on Render

1. **Log in to Render** and click "New +" → "Web Service"

2. **Connect your repository**:
   - Select your GitHub repository
   - Grant Render access if prompted

3. **Configure the service**:
   - **Name**: `legal-case-similarity-api` (or your preferred name)
   - **Environment**: `Python 3`
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your deployment branch)
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
     ```
   - **Start Command**:
     ```bash
     python uvicorn_production.py
     ```
     Or:
     ```bash
     uvicorn src.api.main:app --host 0.0.0.0 --port $PORT --workers 4
     ```

4. **Set environment variables**:
   - Click "Advanced" → "Add Environment Variable"
   - Add the following variables:
     ```
     HOST=0.0.0.0
     PORT=8000
     LOG_LEVEL=warning
     CORS_ORIGINS=https://your-frontend.netlify.app,https://your-frontend.vercel.app
     FRONTEND_URL=https://your-frontend.netlify.app
     PYTHON_VERSION=3.11.0
     ```
   - **Important**: Update `CORS_ORIGINS` with your actual frontend URL(s)

5. **Configure instance type**:
   - Free tier: 512MB RAM (suitable for small deployments)
   - Starter: 2GB RAM (recommended for production)

6. **Create Web Service**:
   - Click "Create Web Service"
   - Render will build and deploy your application
   - Wait for deployment to complete (5-10 minutes)

#### Step 3: Verify Deployment

Once deployed, test your API:

```bash
# Check API info
curl https://your-app.onrender.com/

# Check health endpoint
curl https://your-app.onrender.com/api/health

# View API documentation
# Visit: https://your-app.onrender.com/docs
```

#### Step 4: Configure Custom Domain (Optional)

1. Go to your service settings
2. Click "Custom Domain"
3. Add your domain and follow DNS configuration instructions

#### Using render.yaml (Infrastructure as Code)

Create `render.yaml` in your repository root:

```yaml
services:
  - type: web
    name: legal-case-similarity-api
    env: python
    region: oregon
    plan: starter
    buildCommand: pip install -r requirements.txt && python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
    startCommand: python uvicorn_production.py
    envVars:
      - key: HOST
        value: 0.0.0.0
      - key: PORT
        value: 8000
      - key: LOG_LEVEL
        value: warning
      - key: CORS_ORIGINS
        sync: false  # Set manually in Render dashboard
      - key: FRONTEND_URL
        sync: false  # Set manually in Render dashboard
      - key: PYTHON_VERSION
        value: 3.11.0
    healthCheckPath: /api/health
```

Commit this file and Render will automatically detect and use it.

#### Render-Specific Notes

- **Free tier limitations**: Apps sleep after 15 minutes of inactivity, cold start takes 30-60 seconds
- **Persistent storage**: Use Render Disks for persistent data storage
- **Logs**: View logs in the Render dashboard under "Logs" tab
- **Auto-deploy**: Enable auto-deploy from GitHub for continuous deployment
- **Environment variables**: Can be updated without redeploying

### Docker Deployment

Docker provides a consistent deployment environment across different platforms.

#### Prerequisites

- Docker installed ([get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

#### Step 1: Build Docker Image

The repository includes a `Dockerfile` for the backend:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/cases data/vectors logs

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "uvicorn_production.py"]
```

Build the image:

```bash
docker build -t legal-case-similarity-api .
```

#### Step 2: Run with Docker

Run the container:

```bash
docker run -d \
  --name legal-case-api \
  -p 8000:8000 \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  -e LOG_LEVEL=warning \
  -e CORS_ORIGINS=https://your-frontend.netlify.app \
  -e FRONTEND_URL=https://your-frontend.netlify.app \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  legal-case-similarity-api
```

#### Step 3: Use Docker Compose

Create or update `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: legal-case-api
    ports:
      - "8000:8000"
    environment:
      - HOST=0.0.0.0
      - PORT=8000
      - RELOAD=false
      - LOG_LEVEL=warning
      - CORS_ORIGINS=https://your-frontend.netlify.app,https://your-frontend.vercel.app
      - FRONTEND_URL=https://your-frontend.netlify.app
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

Start the service:

```bash
# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

#### Docker Deployment on Cloud Platforms

**AWS ECS/Fargate**:
```bash
# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag legal-case-similarity-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/legal-case-api:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/legal-case-api:latest
```

**Google Cloud Run**:
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/<project-id>/legal-case-api
gcloud run deploy legal-case-api --image gcr.io/<project-id>/legal-case-api --platform managed
```

**Azure Container Instances**:
```bash
# Create container instance
az container create --resource-group myResourceGroup --name legal-case-api --image legal-case-similarity-api:latest --dns-name-label legal-case-api --ports 8000
```

### Traditional Server Deployment

For deployment on traditional servers (VPS, dedicated servers, on-premises).

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Backend Deployment](#backend-deployment)
  - [Render Deployment](#render-deployment)
  - [Docker Deployment](#docker-deployment)
  - [Traditional Server Deployment](#traditional-server-deployment)
- [Frontend Deployment](#frontend-deployment)
  - [Netlify Deployment](#netlify-deployment)
  - [Vercel Deployment](#vercel-deployment)
  - [GitHub Pages Deployment](#github-pages-deployment)
- [CORS Configuration](#cors-configuration)
- [Local Development Setup](#local-development-setup)
- [System Requirements](#system-requirements)
- [Platform-Specific Installation](#platform-specific-installation)
  - [Linux](#linux)
  - [Windows](#windows)
  - [macOS](#macos)
- [Environment Configuration](#environment-configuration)
- [Troubleshooting](#troubleshooting)

### Traditional Server Deployment

For deployment on traditional servers (VPS, dedicated servers, on-premises).

#### Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Python 3.8+
- Sudo access
- Domain name (optional)

#### Installation Steps

See the [Platform-Specific Installation](#platform-specific-installation) section below for detailed OS-specific instructions.

#### Production Configuration

1. **Create systemd service** `/etc/systemd/system/legal-case-similarity.service`:
   ```ini
   [Unit]
   Description=Legal Case Similarity API
   After=network.target

   [Service]
   Type=simple
   User=www-data
   Group=www-data
   WorkingDirectory=/opt/legal-case-similarity
   Environment="PATH=/opt/legal-case-similarity/venv/bin"
   Environment="HOST=0.0.0.0"
   Environment="PORT=8000"
   Environment="RELOAD=false"
   Environment="LOG_LEVEL=warning"
   Environment="CORS_ORIGINS=https://your-frontend.netlify.app"
   Environment="FRONTEND_URL=https://your-frontend.netlify.app"
   ExecStart=/opt/legal-case-similarity/venv/bin/python uvicorn_production.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and start service**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable legal-case-similarity
   sudo systemctl start legal-case-similarity
   sudo systemctl status legal-case-similarity
   ```

3. **Configure reverse proxy** (see Nginx/Apache sections below)

#### Reverse Proxy Configuration

**Nginx** (`/etc/nginx/sites-available/legal-case-similarity`):

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        
        # CORS headers (if not handled by application)
        add_header 'Access-Control-Allow-Origin' 'https://your-frontend.netlify.app' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/legal-case-similarity /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**Apache** (`/etc/apache2/sites-available/legal-case-similarity.conf`):

```apache
<VirtualHost *:80>
    ServerName api.yourdomain.com

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/

    # CORS headers
    Header always set Access-Control-Allow-Origin "https://your-frontend.netlify.app"
    Header always set Access-Control-Allow-Methods "GET, POST, OPTIONS"
    Header always set Access-Control-Allow-Headers "Content-Type, Authorization"
    Header always set Access-Control-Allow-Credentials "true"

    <Location />
        ProxyTimeout 120
    </Location>

    ErrorLog ${APACHE_LOG_DIR}/legal-case-similarity-error.log
    CustomLog ${APACHE_LOG_DIR}/legal-case-similarity-access.log combined
</VirtualHost>
```

Enable required modules and site:
```bash
sudo a2enmod proxy proxy_http headers
sudo a2ensite legal-case-similarity
sudo systemctl reload apache2
```

## Frontend Deployment

The frontend is a static website that can be deployed on any static hosting platform.

### Netlify Deployment

Netlify provides free static hosting with automatic HTTPS and continuous deployment.

#### Prerequisites

- GitHub account with your repository
- Netlify account (free tier available at [netlify.com](https://www.netlify.com))

#### Step 1: Prepare Frontend

Ensure your `frontend/` directory contains:
- `index.html` (home page)
- `search.html` (search interface)
- `css/` directory with styles
- `js/` directory with JavaScript files
- `netlify.toml` configuration file

#### Step 2: Create netlify.toml

Create `frontend/netlify.toml`:

```toml
[build]
  base = "frontend"
  publish = "."
  command = "bash build.sh"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[build.environment]
  BACKEND_URL = "https://your-api.onrender.com"

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "no-referrer"
    X-XSS-Protection = "1; mode=block"
```

#### Step 3: Create Build Script

Create `frontend/build.sh`:

```bash
#!/bin/bash
# Generate env.js with backend URL from environment variable
cat > js/env.js << EOF
window.ENV = {
    BACKEND_URL: '${BACKEND_URL}'
};
EOF
```

Make it executable:
```bash
chmod +x frontend/build.sh
```

#### Step 4: Deploy to Netlify

**Option A: Deploy via Netlify UI**

1. Log in to Netlify
2. Click "Add new site" → "Import an existing project"
3. Connect to your Git provider (GitHub)
4. Select your repository
5. Configure build settings:
   - **Base directory**: `frontend`
   - **Build command**: `bash build.sh`
   - **Publish directory**: `frontend`
6. Add environment variable:
   - **Key**: `BACKEND_URL`
   - **Value**: `https://your-api.onrender.com`
7. Click "Deploy site"

**Option B: Deploy via Netlify CLI**

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy from frontend directory
cd frontend
netlify deploy --prod
```

#### Step 5: Configure Custom Domain (Optional)

1. Go to "Domain settings" in Netlify
2. Add your custom domain
3. Follow DNS configuration instructions

### Vercel Deployment

Vercel is another excellent platform for static site hosting.

#### Prerequisites

- GitHub account with your repository
- Vercel account (free tier available at [vercel.com](https://vercel.com))

#### Step 1: Create vercel.json

Create `frontend/vercel.json`:

```json
{
  "buildCommand": "bash build.sh",
  "outputDirectory": ".",
  "installCommand": "echo 'No install needed'",
  "framework": null,
  "env": {
    "BACKEND_URL": "https://your-api.onrender.com"
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "Referrer-Policy",
          "value": "no-referrer"
        }
      ]
    }
  ]
}
```

#### Step 2: Deploy to Vercel

**Option A: Deploy via Vercel UI**

1. Log in to Vercel
2. Click "Add New" → "Project"
3. Import your Git repository
4. Configure project:
   - **Framework Preset**: Other
   - **Root Directory**: `frontend`
   - **Build Command**: `bash build.sh`
   - **Output Directory**: `.`
5. Add environment variable:
   - **Key**: `BACKEND_URL`
   - **Value**: `https://your-api.onrender.com`
6. Click "Deploy"

**Option B: Deploy via Vercel CLI**

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from frontend directory
cd frontend
vercel --prod
```

### GitHub Pages Deployment

GitHub Pages provides free static hosting directly from your repository.

#### Prerequisites

- GitHub repository with your code
- GitHub account

#### Step 1: Prepare for GitHub Pages

1. **Create a separate branch** for deployment (optional):
   ```bash
   git checkout -b gh-pages
   ```

2. **Copy frontend files to root** (if deploying from root):
   ```bash
   cp -r frontend/* .
   ```

3. **Create env.js manually**:
   ```javascript
   // js/env.js
   window.ENV = {
       BACKEND_URL: 'https://your-api.onrender.com'
   };
   ```

4. **Commit and push**:
   ```bash
   git add .
   git commit -m "Deploy to GitHub Pages"
   git push origin gh-pages
   ```

#### Step 2: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click "Settings" → "Pages"
3. Under "Source", select:
   - **Branch**: `gh-pages` (or `main`)
   - **Folder**: `/root` (or `/frontend` if using main branch)
4. Click "Save"
5. Your site will be available at `https://username.github.io/repository-name/`

#### Step 3: Configure Custom Domain (Optional)

1. Add a `CNAME` file with your domain:
   ```bash
   echo "yourdomain.com" > CNAME
   ```
2. Configure DNS records at your domain provider
3. Enable HTTPS in GitHub Pages settings

#### GitHub Actions for Automated Deployment

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Generate env.js
        run: |
          cd frontend
          cat > js/env.js << EOF
          window.ENV = {
              BACKEND_URL: '${{ secrets.BACKEND_URL }}'
          };
          EOF
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./frontend
```

Add `BACKEND_URL` to repository secrets in GitHub settings.

## CORS Configuration

Cross-Origin Resource Sharing (CORS) is essential for the frontend to communicate with the backend when hosted on different domains.

### Understanding CORS

CORS is a security mechanism that allows or restricts web applications running at one origin (domain) to access resources from a different origin. Since your frontend and backend are deployed separately, CORS must be properly configured.

### Backend CORS Configuration

The backend uses FastAPI's `CORSMiddleware` to handle CORS. Configuration is in `src/api/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware
import os

# Get allowed origins from environment variable
allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # List of allowed origins
    allow_credentials=True,          # Allow cookies and auth headers
    allow_methods=["*"],             # Allow all HTTP methods
    allow_headers=["*"],             # Allow all headers
)
```

### CORS Environment Variables

Set the `CORS_ORIGINS` environment variable based on your deployment:

**Development (Local)**:
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000
```

**Production (Single Frontend)**:
```bash
CORS_ORIGINS=https://your-frontend.netlify.app
```

**Production (Multiple Frontends)**:
```bash
CORS_ORIGINS=https://your-frontend.netlify.app,https://your-frontend.vercel.app,https://yourdomain.com
```

**Development (Allow All - NOT for production)**:
```bash
CORS_ORIGINS=*
```

### Setting CORS Origins by Platform

**Render**:
1. Go to your service dashboard
2. Click "Environment" tab
3. Add environment variable:
   - **Key**: `CORS_ORIGINS`
   - **Value**: `https://your-frontend.netlify.app`
4. Save changes (triggers redeploy)

**Docker**:
```bash
docker run -e CORS_ORIGINS=https://your-frontend.netlify.app ...
```

Or in `docker-compose.yml`:
```yaml
environment:
  - CORS_ORIGINS=https://your-frontend.netlify.app,https://yourdomain.com
```

**Traditional Server**:
Add to systemd service file or `.env`:
```bash
CORS_ORIGINS=https://your-frontend.netlify.app
```

### Verifying CORS Configuration

Test CORS headers with curl:

```bash
# Test preflight request
curl -X OPTIONS https://your-api.onrender.com/api/upload \
  -H "Origin: https://your-frontend.netlify.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v

# Expected response headers:
# Access-Control-Allow-Origin: https://your-frontend.netlify.app
# Access-Control-Allow-Methods: GET, POST, OPTIONS, ...
# Access-Control-Allow-Headers: Content-Type, ...
# Access-Control-Allow-Credentials: true
```

Test actual request:

```bash
curl -X GET https://your-api.onrender.com/api/health \
  -H "Origin: https://your-frontend.netlify.app" \
  -v

# Should include:
# Access-Control-Allow-Origin: https://your-frontend.netlify.app
```

### Frontend CORS Handling

The frontend automatically handles CORS by including the origin in requests. No special configuration needed in the frontend code.

**Error Handling for CORS Issues**:

The frontend includes error handling for CORS failures in `frontend/js/app.js`:

```javascript
async uploadFile(file) {
    try {
        const response = await fetch(endpoint, { method: 'POST', body: formData });
        // ... handle response
    } catch (error) {
        if (error.message.includes('CORS') || error.message.includes('Failed to fetch')) {
            this.showError(
                'Unable to connect to the API. This may be a CORS configuration issue. ' +
                'Please check that the backend URL is correct and CORS is properly configured.'
            );
        }
    }
}
```

## Local Development Setup

For local development with separated frontend and backend.

### Backend Setup

1. **Clone repository**:
   ```bash
   git clone <repository-url>
   cd legal-case-similarity
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
   ```

4. **Set environment variables**:
   ```bash
   export CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000
   export FRONTEND_URL=http://localhost:3000
   ```

5. **Run backend**:
   ```bash
   python run_api.py
   ```

   Backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Create env.js for local development**:
   ```javascript
   // frontend/js/env.js
   window.ENV = {
       BACKEND_URL: 'http://localhost:8000'
   };
   ```

3. **Serve frontend** (choose one method):

   **Option A: Python HTTP Server**:
   ```bash
   python -m http.server 3000
   ```

   **Option B: Node.js http-server**:
   ```bash
   npx http-server -p 3000
   ```

   **Option C: PHP Built-in Server**:
   ```bash
   php -S localhost:3000
   ```

   Frontend will be available at `http://localhost:3000`

### Testing Local Setup

1. **Open frontend**: Navigate to `http://localhost:3000`
2. **Test home page**: Verify home page loads correctly
3. **Test navigation**: Click "Get Started" to go to search page
4. **Test API connection**: Upload a PDF file
5. **Check browser console**: Verify no CORS errors
6. **Check backend logs**: Verify requests are received

### Development Workflow

1. **Make backend changes**: Edit files in `src/`
2. **Restart backend**: Stop and restart `run_api.py` (or use `--reload` flag)
3. **Make frontend changes**: Edit files in `frontend/`
4. **Refresh browser**: Changes are immediately visible
5. **Test integration**: Verify frontend-backend communication works

## System Requirements

- **Python**: 3.8 or higher
- **RAM**: Minimum 2GB, recommended 4GB for processing large documents
- **Disk Space**: Minimum 1GB for application and dependencies, plus storage for case repository
- **Network**: Port 8000 (default) or custom port for API access

## Platform-Specific Installation

### Linux

#### Ubuntu/Debian

1. **Install Python and pip**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Download NLTK data**:
   ```bash
   python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
   ```

5. **Verify installation**:
   ```bash
   python verify_setup.py
   ```

#### CentOS/RHEL/Fedora

1. **Install Python and pip**:
   ```bash
   sudo dnf install python3 python3-pip python3-virtualenv
   # Or for older versions: sudo yum install python3 python3-pip
   ```

2. **Follow steps 2-5 from Ubuntu/Debian section above**

#### Additional Linux Notes

- For production deployments, consider using systemd service files (see Production Deployment section)
- Ensure firewall allows traffic on the configured port:
  ```bash
  sudo ufw allow 8000/tcp  # Ubuntu/Debian
  sudo firewall-cmd --permanent --add-port=8000/tcp  # CentOS/RHEL
  sudo firewall-cmd --reload
  ```

### Windows

#### Windows 10/11

1. **Install Python**:
   - Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
   - Verify installation: `python --version`

2. **Create virtual environment**:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```cmd
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Download NLTK data**:
   ```cmd
   python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
   ```

5. **Verify installation**:
   ```cmd
   python verify_setup.py
   ```

#### Windows-Specific Notes

- If you encounter SSL certificate errors during pip install, try:
  ```cmd
  pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
  ```
- For production on Windows Server, consider using IIS with FastCGI or running as a Windows Service
- Ensure Windows Defender or antivirus allows Python and the application to run

### macOS

#### macOS 10.15+ (Catalina and later)

1. **Install Homebrew** (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python**:
   ```bash
   brew install python@3.11
   ```

3. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Download NLTK data**:
   ```bash
   python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
   ```

6. **Verify installation**:
   ```bash
   python verify_setup.py
   ```

#### macOS-Specific Notes

- On Apple Silicon (M1/M2), some dependencies may require Rosetta 2 or native ARM builds
- If you encounter issues with PyMuPDF, try: `pip install --upgrade pymupdf`
- For production deployments, consider using launchd for service management

## Production Deployment

### Configuration for Production

1. **Update CORS settings** in `src/api/main.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],  # Specify your domain
       allow_credentials=True,
       allow_methods=["GET", "POST"],
       allow_headers=["*"],
   )
   ```

2. **Set environment variables**:
   ```bash
   export HOST="0.0.0.0"
   export PORT="8000"
   export RELOAD="false"
   export LOG_LEVEL="warning"
   ```

3. **Use production-ready server configuration**:
   ```bash
   python run_api.py
   ```

### Running with Uvicorn (Production Mode)

For production deployments, use the following Uvicorn configuration:

```bash
uvicorn src.api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level warning \
  --no-access-log \
  --proxy-headers \
  --forwarded-allow-ips='*'
```

**Configuration Options**:
- `--workers`: Number of worker processes (recommended: 2-4 × CPU cores)
- `--log-level`: Set to `warning` or `error` for production
- `--no-access-log`: Disable access logs for better performance
- `--proxy-headers`: Enable if behind a reverse proxy (nginx, Apache)
- `--forwarded-allow-ips`: Configure trusted proxy IPs

### Using Gunicorn with Uvicorn Workers

For enhanced production stability, use Gunicorn with Uvicorn workers:

1. **Install Gunicorn**:
   ```bash
   pip install gunicorn
   ```

2. **Run with Gunicorn**:
   ```bash
   gunicorn src.api.main:app \
     --workers 4 \
     --worker-class uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:8000 \
     --timeout 120 \
     --access-logfile logs/access.log \
     --error-logfile logs/error.log
   ```

### Systemd Service (Linux)

Create a systemd service file for automatic startup and management:

1. **Create service file** `/etc/systemd/system/legal-case-similarity.service`:
   ```ini
   [Unit]
   Description=Legal Case Similarity Web Application
   After=network.target

   [Service]
   Type=simple
   User=www-data
   Group=www-data
   WorkingDirectory=/opt/legal-case-similarity
   Environment="PATH=/opt/legal-case-similarity/venv/bin"
   Environment="HOST=0.0.0.0"
   Environment="PORT=8000"
   Environment="RELOAD=false"
   Environment="LOG_LEVEL=warning"
   ExecStart=/opt/legal-case-similarity/venv/bin/python run_api.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and start service**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable legal-case-similarity
   sudo systemctl start legal-case-similarity
   sudo systemctl status legal-case-similarity
   ```

3. **View logs**:
   ```bash
   sudo journalctl -u legal-case-similarity -f
   ```

### Reverse Proxy Configuration

#### Nginx

Create `/etc/nginx/sites-available/legal-case-similarity`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    location /static {
        alias /opt/legal-case-similarity/static;
        expires 30d;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/legal-case-similarity /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Apache

Enable required modules and create virtual host:

```bash
sudo a2enmod proxy proxy_http headers
```

Create `/etc/apache2/sites-available/legal-case-similarity.conf`:

```apache
<VirtualHost *:80>
    ServerName yourdomain.com

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/

    <Location />
        ProxyTimeout 120
    </Location>

    ErrorLog ${APACHE_LOG_DIR}/legal-case-similarity-error.log
    CustomLog ${APACHE_LOG_DIR}/legal-case-similarity-access.log combined
</VirtualHost>
```

Enable the site:
```bash
sudo a2ensite legal-case-similarity
sudo systemctl reload apache2
```

### Docker Deployment (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/cases data/vectors logs

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "run_api.py"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - HOST=0.0.0.0
      - PORT=8000
      - RELOAD=false
      - LOG_LEVEL=warning
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
```

Build and run:
```bash
docker-compose up -d
```

## Environment Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |
| `RELOAD` | `true` | Enable auto-reload (dev only) |
| `LOG_LEVEL` | `info` | Logging level (debug, info, warning, error) |

### Configuration Files

- `src/config/settings.py`: Application settings
- `src/config/logging_config.py`: Logging configuration
- `data/legal_vocabulary.json`: Legal terms vocabulary
- `data/cases_metadata.json`: Case repository metadata

## Troubleshooting

### Common Issues

#### CORS Errors

**Error**: `Access to fetch at 'https://api.example.com/api/upload' from origin 'https://frontend.example.com' has been blocked by CORS policy`

**Symptoms**:
- Frontend cannot connect to backend
- Browser console shows CORS errors
- Network tab shows failed preflight (OPTIONS) requests

**Solutions**:

1. **Verify CORS_ORIGINS environment variable**:
   ```bash
   # Check current value on backend
   curl https://your-api.onrender.com/api/health | jq '.statistics.cors_origins'
   ```

2. **Ensure frontend URL is in CORS_ORIGINS**:
   ```bash
   # Backend environment variable should include frontend URL
   CORS_ORIGINS=https://your-frontend.netlify.app,https://your-frontend.vercel.app
   ```

3. **Check for trailing slashes**:
   - Frontend URL: `https://example.com` (no trailing slash)
   - CORS origin: `https://example.com` (must match exactly)

4. **Verify protocol (http vs https)**:
   - Development: `http://localhost:3000`
   - Production: `https://your-frontend.netlify.app`
   - Protocol must match exactly

5. **Test CORS headers**:
   ```bash
   curl -X OPTIONS https://your-api.onrender.com/api/upload \
     -H "Origin: https://your-frontend.netlify.app" \
     -H "Access-Control-Request-Method: POST" \
     -v
   ```

6. **Check browser console for specific error**:
   - Open Developer Tools (F12)
   - Go to Console tab
   - Look for detailed CORS error message
   - Verify the origin being sent matches CORS_ORIGINS

7. **Restart backend after changing CORS_ORIGINS**:
   - Render: Changes trigger automatic redeploy
   - Docker: `docker-compose restart`
   - Systemd: `sudo systemctl restart legal-case-similarity`

8. **Temporary debugging - Allow all origins** (development only):
   ```bash
   CORS_ORIGINS=*
   ```
   **WARNING**: Never use `*` in production!

**Common CORS Mistakes**:
- ❌ `CORS_ORIGINS=https://example.com/` (trailing slash)
- ✅ `CORS_ORIGINS=https://example.com`
- ❌ `CORS_ORIGINS=example.com` (missing protocol)
- ✅ `CORS_ORIGINS=https://example.com`
- ❌ Multiple origins without commas: `https://a.com https://b.com`
- ✅ Multiple origins with commas: `https://a.com,https://b.com`

#### Frontend Cannot Connect to Backend

**Error**: `Failed to fetch` or `Network request failed`

**Solutions**:

1. **Verify backend URL in frontend**:
   - Check `frontend/js/env.js` contains correct `BACKEND_URL`
   - Verify URL is accessible: `curl https://your-api.onrender.com/api/health`

2. **Check backend is running**:
   ```bash
   curl https://your-api.onrender.com/
   ```

3. **Verify HTTPS/HTTP**:
   - Frontend on HTTPS cannot call backend on HTTP (mixed content)
   - Both should use HTTPS in production

4. **Check browser console**:
   - Look for specific error messages
   - Check Network tab for failed requests
   - Verify request URL is correct

5. **Test backend directly**:
   ```bash
   # Should return API info
   curl https://your-api.onrender.com/
   
   # Should return health status
   curl https://your-api.onrender.com/api/health
   ```

#### Backend Not Responding (Render)

**Error**: Backend returns 502 Bad Gateway or times out

**Solutions**:

1. **Check Render logs**:
   - Go to Render dashboard
   - Click on your service
   - View "Logs" tab for errors

2. **Verify build completed successfully**:
   - Check "Events" tab for build status
   - Ensure NLTK downloads completed

3. **Check health endpoint**:
   ```bash
   curl https://your-app.onrender.com/api/health
   ```

4. **Verify environment variables are set**:
   - Go to "Environment" tab
   - Ensure all required variables are present

5. **Check instance resources**:
   - Free tier may be sleeping (cold start takes 30-60s)
   - Upgrade to paid tier for always-on service

6. **Review start command**:
   - Ensure start command is correct in Render settings
   - Should be: `python uvicorn_production.py` or similar

#### File Upload Fails

**Error**: Upload fails with 413 Payload Too Large or timeout

**Solutions**:

1. **Check file size limit**:
   - Default limit: 10MB
   - Verify file is under limit

2. **Increase timeout** (if processing takes too long):
   - Render: Increase timeout in service settings
   - Nginx: Increase `proxy_read_timeout`
   - Frontend: Increase fetch timeout

3. **Check backend logs** for specific error:
   ```bash
   # Render: View logs in dashboard
   # Docker: docker-compose logs -f
   # Systemd: sudo journalctl -u legal-case-similarity -f
   ```

4. **Verify PDF is valid**:
   - Try with a different PDF
   - Ensure PDF is not corrupted

#### Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Linux/macOS
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

Or change the port:
```bash
export PORT=8001
python run_api.py
```

#### NLTK Data Not Found

**Error**: `Resource stopwords not found`

**Solution**:
```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
```

#### Permission Denied (Linux)

**Error**: `Permission denied` when accessing files

**Solution**:
```bash
sudo chown -R $USER:$USER /opt/legal-case-similarity
chmod -R 755 /opt/legal-case-similarity
```

#### PyMuPDF Installation Issues

**Error**: Issues installing PyMuPDF

**Solution**:
```bash
# Try upgrading pip first
pip install --upgrade pip setuptools wheel

# Then install PyMuPDF
pip install --upgrade pymupdf
```

#### Memory Issues with Large PDFs

**Error**: Out of memory when processing large documents

**Solution**:
- Increase system memory allocation
- Process documents in smaller batches
- Configure worker processes based on available RAM
- For Render: Upgrade to a plan with more RAM

#### Environment Variables Not Loading

**Error**: Application uses default values instead of environment variables

**Solutions**:

1. **Verify environment variables are set**:
   ```bash
   # Render: Check "Environment" tab
   # Docker: Check docker-compose.yml or docker run command
   # Systemd: Check service file
   ```

2. **Check variable names** (case-sensitive):
   - `CORS_ORIGINS` (not `CORS_ORIGIN` or `cors_origins`)
   - `FRONTEND_URL` (not `FRONTEND_URI`)

3. **Restart application** after setting variables

4. **Check application logs** for loaded configuration:
   - Backend logs CORS configuration on startup

#### SSL/HTTPS Issues

**Error**: Mixed content warnings or HTTPS errors

**Solutions**:

1. **Ensure both frontend and backend use HTTPS** in production
2. **Use platform-provided SSL**:
   - Render: Automatic HTTPS
   - Netlify/Vercel: Automatic HTTPS
   - Traditional server: Use Let's Encrypt

3. **Configure custom domain** with SSL certificate

4. **Update all URLs to use HTTPS** in configuration

### Debugging Tips

1. **Enable debug logging**:
   ```bash
   LOG_LEVEL=debug
   ```

2. **Check API health endpoint**:
   ```bash
   curl https://your-api.onrender.com/api/health
   ```
   Returns CORS configuration and system status

3. **Test CORS with browser**:
   - Open browser console (F12)
   - Go to Network tab
   - Upload a file
   - Check request/response headers

4. **Use browser CORS extension** (development only):
   - Install "CORS Unblock" or similar extension
   - Use only for debugging, not as a solution

5. **Check backend logs**:
   - Render: Dashboard → Logs
   - Docker: `docker-compose logs -f`
   - Systemd: `sudo journalctl -u legal-case-similarity -f`

6. **Verify frontend configuration**:
   - Open browser console
   - Type: `window.AppConfig.getBackendUrl()`
   - Should return correct backend URL

### Getting Help

- Check application logs in `logs/` directory (traditional deployment)
- Run verification script: `python verify_setup.py`
- Review API health endpoint: `http://localhost:8000/api/health`
- Check Render logs in dashboard (Render deployment)
- Review browser console for frontend errors
- Consult the main README.md for additional documentation

## Production Deployment (Legacy)

**Note**: The sections below describe traditional deployment methods. For modern cloud deployment, see the [Backend Deployment](#backend-deployment) and [Frontend Deployment](#frontend-deployment) sections above.

### Configuration for Production

1. **Update CORS settings** via environment variable:
   ```bash
   export CORS_ORIGINS=https://yourdomain.com
   export FRONTEND_URL=https://yourdomain.com
   ```

2. **Set environment variables**:
   ```bash
   export HOST="0.0.0.0"
   export PORT="8000"
   export RELOAD="false"
   export LOG_LEVEL="warning"
   ```

3. **Use production-ready server configuration**:
   ```bash
   python uvicorn_production.py
   ```

### Running with Uvicorn (Production Mode)

For production deployments, use the following Uvicorn configuration:

```bash
uvicorn src.api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level warning \
  --no-access-log \
  --proxy-headers \
  --forwarded-allow-ips='*'
```

**Configuration Options**:
- `--workers`: Number of worker processes (recommended: 2-4 × CPU cores)
- `--log-level`: Set to `warning` or `error` for production
- `--no-access-log`: Disable access logs for better performance
- `--proxy-headers`: Enable if behind a reverse proxy (nginx, Apache)
- `--forwarded-allow-ips`: Configure trusted proxy IPs

### Using Gunicorn with Uvicorn Workers

For enhanced production stability, use Gunicorn with Uvicorn workers:

1. **Install Gunicorn**:
   ```bash
   pip install gunicorn
   ```

2. **Run with Gunicorn**:
   ```bash
   gunicorn src.api.main:app \
     --workers 4 \
     --worker-class uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:8000 \
     --timeout 120 \
     --access-logfile logs/access.log \
     --error-logfile logs/error.log
   ```

### Systemd Service (Linux)

See [Traditional Server Deployment](#traditional-server-deployment) section above for systemd configuration.

### Reverse Proxy Configuration

See [Traditional Server Deployment](#traditional-server-deployment) section above for Nginx and Apache configuration.

### Docker Deployment (Optional)

**Note**: For detailed Docker deployment instructions, see the [Docker Deployment](#docker-deployment) section above.

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/cases data/vectors logs

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "uvicorn_production.py"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - HOST=0.0.0.0
      - PORT=8000
      - RELOAD=false
      - LOG_LEVEL=warning
      - CORS_ORIGINS=https://your-frontend.netlify.app
      - FRONTEND_URL=https://your-frontend.netlify.app
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
```

Build and run:
```bash
docker-compose up -d
```


## Performance Optimization

### Backend Performance

1. **Adjust worker count** based on CPU cores:
   ```bash
   # Calculate optimal workers: (2 × CPU cores) + 1
   # For Render/production
   --workers 4  # Adjust based on instance size
   ```

2. **Enable response caching** for frequently accessed cases

3. **Use SSD storage** for case repository and vector storage

4. **Monitor resource usage**:
   ```bash
   # Linux
   htop
   
   # Check application logs
   tail -f logs/app.log
   
   # Render: View metrics in dashboard
   ```

5. **Optimize NLTK data loading**:
   - Download only required NLTK data
   - Cache NLTK data in Docker image

### Frontend Performance

1. **Use CDN** for static assets (Netlify/Vercel provide this automatically)

2. **Enable caching** headers for static files

3. **Minimize JavaScript** and CSS files (optional)

4. **Use lazy loading** for images

5. **Enable compression** (gzip/brotli) - automatic on most platforms

### Database and Storage

1. **Use persistent storage** for case repository:
   - Render: Use Render Disks
   - Docker: Use volumes
   - Traditional: Use dedicated storage partition

2. **Implement backup strategy** for data directory

3. **Monitor disk usage** and set up alerts

## Security Considerations

### Backend Security

1. **Configure CORS properly**:
   - ✅ Use specific origins in production
   - ❌ Never use `CORS_ORIGINS=*` in production

2. **Use HTTPS** everywhere:
   - Render: Automatic HTTPS
   - Traditional server: Use Let's Encrypt
   - Never serve production over HTTP

3. **Implement rate limiting** for API endpoints:
   ```python
   # Add to src/api/main.py
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   
   @app.post("/api/upload")
   @limiter.limit("10/minute")
   async def upload_file(...):
       ...
   ```

4. **Restrict file upload sizes** (default: 10MB):
   ```python
   # Already configured in FastAPI
   app.add_middleware(
       RequestSizeLimitMiddleware,
       max_request_size=10 * 1024 * 1024  # 10MB
   )
   ```

5. **Run application as non-root user**:
   - Docker: Use non-root user in Dockerfile
   - Systemd: Configure `User=www-data`

6. **Keep dependencies updated**:
   ```bash
   pip install --upgrade -r requirements.txt
   pip-audit  # Check for vulnerabilities
   ```

7. **Enable firewall** and restrict access:
   ```bash
   # Only allow necessary ports
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

8. **Use environment variables** for sensitive configuration:
   - Never commit secrets to repository
   - Use platform secret management (Render environment variables)

9. **Implement authentication** if handling sensitive documents:
   - Add API key authentication
   - Use OAuth2 for user authentication
   - Implement JWT tokens

10. **Regular security audits**:
    ```bash
    # Check for dependency vulnerabilities
    pip-audit
    
    # Scan Docker images
    docker scan legal-case-similarity-api
    ```

### Frontend Security

1. **Set security headers** (configured in netlify.toml/vercel.json):
   - `X-Frame-Options: DENY`
   - `X-Content-Type-Options: nosniff`
   - `Referrer-Policy: no-referrer`
   - `Content-Security-Policy` (optional)

2. **Validate user input** before sending to backend

3. **Sanitize displayed content** to prevent XSS

4. **Use HTTPS only** - no mixed content

5. **Implement Content Security Policy**:
   ```html
   <meta http-equiv="Content-Security-Policy" 
         content="default-src 'self'; 
                  connect-src 'self' https://your-api.onrender.com; 
                  script-src 'self' 'unsafe-inline';">
   ```

## Monitoring and Maintenance

### Health Checks

**Backend Health Monitoring**:

```bash
# Manual health check
curl https://your-api.onrender.com/api/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "components": {
    "api": "operational",
    "case_repository": "operational",
    "vectorizer": "operational"
  },
  "statistics": {
    "total_cases": 15,
    "cors_origins": "https://your-frontend.netlify.app",
    "frontend_url": "https://your-frontend.netlify.app"
  }
}
```

**Automated Monitoring**:

1. **Render**: Built-in health checks
   - Configure health check path: `/api/health`
   - Set check interval: 30 seconds

2. **UptimeRobot** (free external monitoring):
   - Monitor: `https://your-api.onrender.com/api/health`
   - Alert on downtime

3. **Custom monitoring script**:
   ```bash
   #!/bin/bash
   # monitor.sh
   HEALTH_URL="https://your-api.onrender.com/api/health"
   
   response=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)
   
   if [ $response -ne 200 ]; then
       echo "API is down! Status: $response"
       # Send alert (email, Slack, etc.)
   fi
   ```

### Log Management

**Backend Logs**:

1. **Render**: View logs in dashboard
   - Real-time logs in "Logs" tab
   - Download logs for analysis

2. **Docker**: Access container logs
   ```bash
   docker-compose logs -f api
   docker-compose logs --tail=100 api
   ```

3. **Traditional server**: Use systemd/log files
   ```bash
   sudo journalctl -u legal-case-similarity -f
   tail -f logs/app.log
   tail -f logs/error.log
   ```

**Log Rotation** (traditional server):

Create `/etc/logrotate.d/legal-case-similarity`:
```
/opt/legal-case-similarity/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload legal-case-similarity > /dev/null 2>&1 || true
    endscript
}
```

**Frontend Logs**:

1. **Netlify/Vercel**: View function logs in dashboard
2. **Browser console**: Check for JavaScript errors
3. **Analytics**: Use Google Analytics or similar for user tracking

### Backup Strategy

**What to Backup**:
- Case repository: `data/cases/`
- Metadata: `data/cases_metadata.json`
- Vectors: `data/vectors/`
- Configuration files: `.env`, `render.yaml`
- Application logs (optional)

**Backup Methods**:

1. **Render Disks** (persistent storage):
   - Automatic snapshots available
   - Manual backups via dashboard

2. **Cloud Storage** (S3, Google Cloud Storage):
   ```bash
   # Backup to S3
   aws s3 sync data/ s3://your-bucket/backups/data/
   ```

3. **Local Backups** (traditional server):
   ```bash
   #!/bin/bash
   # backup.sh
   BACKUP_DIR="/backups/legal-case-similarity"
   DATE=$(date +%Y%m%d_%H%M%S)
   
   tar -czf $BACKUP_DIR/backup_$DATE.tar.gz \
       data/ \
       logs/ \
       .env
   
   # Keep only last 7 backups
   ls -t $BACKUP_DIR/backup_*.tar.gz | tail -n +8 | xargs rm -f
   ```

4. **Automated Backups** (cron job):
   ```bash
   # Add to crontab: crontab -e
   0 2 * * * /opt/legal-case-similarity/backup.sh
   ```

### Updates and Upgrades

**Backend Updates**:

1. **Render** (automatic):
   - Enable auto-deploy from GitHub
   - Push to main branch triggers deployment
   - Monitor deployment in dashboard

2. **Docker**:
   ```bash
   # Pull latest code
   git pull origin main
   
   # Rebuild and restart
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

3. **Traditional server**:
   ```bash
   # Backup first
   ./backup.sh
   
   # Pull latest code
   git pull origin main
   
   # Update dependencies
   source venv/bin/activate
   pip install --upgrade -r requirements.txt
   
   # Run tests
   pytest
   
   # Restart service
   sudo systemctl restart legal-case-similarity
   ```

**Frontend Updates**:

1. **Netlify/Vercel** (automatic):
   - Push to main branch triggers deployment
   - Preview deployments for pull requests

2. **Manual deployment**:
   ```bash
   cd frontend
   netlify deploy --prod
   # or
   vercel --prod
   ```

**Update Checklist**:
- [ ] Backup current installation
- [ ] Review changelog/release notes
- [ ] Update dependencies
- [ ] Run tests locally
- [ ] Deploy to staging (if available)
- [ ] Test thoroughly
- [ ] Deploy to production
- [ ] Monitor logs for errors
- [ ] Verify health check passes

### Performance Monitoring

**Metrics to Monitor**:
- Response time (API endpoints)
- Error rate (4xx, 5xx responses)
- CPU usage
- Memory usage
- Disk usage
- Request rate
- CORS errors

**Monitoring Tools**:

1. **Render Dashboard**: Built-in metrics
2. **Application Performance Monitoring** (APM):
   - New Relic
   - Datadog
   - Sentry (for error tracking)

3. **Custom metrics endpoint**:
   ```bash
   curl https://your-api.onrender.com/api/performance
   ```

## Performance Benchmarks

Expected performance on recommended hardware:

**Backend (Render Starter Plan - 2GB RAM)**:
- PDF text extraction: < 2 seconds per document
- Similarity search (1000 cases): < 5 seconds
- Concurrent requests: 10-20 requests/second
- Memory usage: 500MB-2GB depending on repository size
- Cold start (free tier): 30-60 seconds

**Frontend (Static Hosting)**:
- Initial page load: < 2 seconds
- Time to interactive: < 3 seconds
- Served from CDN: < 100ms globally

**Network**:
- API request latency: 100-500ms (depends on region)
- File upload time: Depends on file size and connection speed
- CORS preflight: < 100ms

## Cost Estimates

**Render (Backend)**:
- Free tier: $0/month (with limitations)
- Starter: $7/month (recommended for production)
- Standard: $25/month (for high traffic)

**Netlify/Vercel (Frontend)**:
- Free tier: $0/month (sufficient for most use cases)
- Pro: $19-20/month (for custom domains and advanced features)

**Total Monthly Cost** (production):
- Minimum: $7/month (Render Starter + Netlify Free)
- Recommended: $26/month (Render Starter + Netlify Pro)

## License and Support

Refer to the main README.md for license information and support channels.

For deployment-specific issues:
- Render: [Render Documentation](https://render.com/docs)
- Netlify: [Netlify Documentation](https://docs.netlify.com)
- Vercel: [Vercel Documentation](https://vercel.com/docs)
- Docker: [Docker Documentation](https://docs.docker.com)

## Appendix: Quick Reference

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HOST` | No | `0.0.0.0` | Server bind address |
| `PORT` | No | `8000` | Server port |
| `LOG_LEVEL` | No | `info` | Logging level (debug, info, warning, error) |
| `RELOAD` | No | `false` | Enable auto-reload (development only) |
| `CORS_ORIGINS` | **Yes** | `*` | Comma-separated list of allowed origins |
| `FRONTEND_URL` | **Yes** | - | Frontend application URL |
| `PYTHON_VERSION` | No | `3.11.0` | Python version (Render) |

### Common Commands Reference

**Backend**:
```bash
# Local development
python run_api.py

# Production (Uvicorn)
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Docker
docker-compose up -d
docker-compose logs -f
docker-compose down

# Health check
curl http://localhost:8000/api/health
```

**Frontend**:
```bash
# Local development
cd frontend
python -m http.server 3000

# Deploy to Netlify
netlify deploy --prod

# Deploy to Vercel
vercel --prod
```

**Testing CORS**:
```bash
# Test preflight
curl -X OPTIONS https://api.example.com/api/upload \
  -H "Origin: https://frontend.example.com" \
  -H "Access-Control-Request-Method: POST" \
  -v

# Test actual request
curl -X GET https://api.example.com/api/health \
  -H "Origin: https://frontend.example.com" \
  -v
```

### Deployment Checklist

**Backend Deployment**:
- [ ] Set `CORS_ORIGINS` environment variable
- [ ] Set `FRONTEND_URL` environment variable
- [ ] Set `LOG_LEVEL=warning` for production
- [ ] Configure health check endpoint
- [ ] Enable HTTPS
- [ ] Test API endpoints
- [ ] Monitor logs for errors

**Frontend Deployment**:
- [ ] Set `BACKEND_URL` environment variable
- [ ] Create `env.js` with backend URL
- [ ] Test home page loads
- [ ] Test navigation works
- [ ] Test API connection
- [ ] Verify no CORS errors
- [ ] Test on multiple browsers
- [ ] Test on mobile devices

**Integration Testing**:
- [ ] Frontend can reach backend
- [ ] CORS requests succeed
- [ ] File upload works
- [ ] Results display correctly
- [ ] Error handling works
- [ ] Download functionality works
