# Deployment Guide - Legal Case Similarity Web Application

This guide provides comprehensive instructions for deploying the Legal Case Similarity Web Application across different platforms and environments.

## Table of Contents

- [System Requirements](#system-requirements)
- [Platform-Specific Installation](#platform-specific-installation)
  - [Linux](#linux)
  - [Windows](#windows)
  - [macOS](#macos)
- [Production Deployment](#production-deployment)
- [Environment Configuration](#environment-configuration)
- [Troubleshooting](#troubleshooting)

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

### Performance Optimization

1. **Adjust worker count** based on CPU cores:
   ```bash
   # Calculate optimal workers: (2 × CPU cores) + 1
   export WORKERS=$((2 * $(nproc) + 1))
   ```

2. **Enable response caching** for frequently accessed cases

3. **Use SSD storage** for case repository and vector storage

4. **Monitor resource usage**:
   ```bash
   # Linux
   htop
   
   # Check application logs
   tail -f logs/app.log
   ```

### Getting Help

- Check application logs in `logs/` directory
- Run verification script: `python verify_setup.py`
- Review API health endpoint: `http://localhost:8000/api/health`
- Consult the main README.md for additional documentation

## Security Considerations

1. **Update CORS origins** to specific domains in production
2. **Use HTTPS** with SSL/TLS certificates (Let's Encrypt recommended)
3. **Implement rate limiting** for API endpoints
4. **Restrict file upload sizes** (default: 10MB)
5. **Run application as non-root user** in production
6. **Keep dependencies updated**: `pip install --upgrade -r requirements.txt`
7. **Enable firewall** and restrict access to necessary ports only
8. **Use environment variables** for sensitive configuration
9. **Implement authentication** if handling sensitive legal documents
10. **Regular security audits** and dependency vulnerability scanning

## Monitoring and Maintenance

### Health Checks

Monitor application health:
```bash
curl http://localhost:8000/api/health
```

### Log Rotation

Configure log rotation to prevent disk space issues:

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

### Backup Strategy

Regular backups of:
- Case repository: `data/cases/`
- Metadata: `data/cases_metadata.json`
- Vectors: `data/vectors/`
- Configuration files

### Updates and Upgrades

1. **Backup current installation**
2. **Pull latest code** from repository
3. **Update dependencies**: `pip install --upgrade -r requirements.txt`
4. **Run tests**: `pytest`
5. **Restart service**: `sudo systemctl restart legal-case-similarity`

## Performance Benchmarks

Expected performance on recommended hardware:
- PDF text extraction: < 2 seconds per document
- Similarity search (1000 cases): < 5 seconds
- Concurrent requests: 10-20 requests/second
- Memory usage: 500MB-2GB depending on repository size

## License and Support

Refer to the main README.md for license information and support channels.
