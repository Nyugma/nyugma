# Quick Deployment Guide

This guide provides quick deployment instructions for common scenarios.

## Prerequisites

- Python 3.8 or higher
- 2GB RAM minimum (4GB recommended)
- 1GB disk space minimum

## Quick Start (Development)

### Linux / macOS
```bash
chmod +x install.sh
./install.sh
source venv/bin/activate
python run_api.py
```

### Windows
```cmd
install.bat
venv\Scripts\activate.bat
python run_api.py
```

Access the application at: http://localhost:8000

## Production Deployment

### Option 1: Direct Python (Simplest)

```bash
# Install
./install.sh  # or install.bat on Windows

# Configure
export HOST=0.0.0.0
export PORT=8000
export WORKERS=4
export LOG_LEVEL=warning
export RELOAD=false

# Run
python uvicorn_production.py
```

### Option 2: Systemd Service (Linux)

```bash
# Install application
sudo mkdir -p /opt/legal-case-similarity
sudo cp -r . /opt/legal-case-similarity/
cd /opt/legal-case-similarity
./install.sh

# Install service
sudo cp legal-case-similarity.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable legal-case-similarity
sudo systemctl start legal-case-similarity

# Check status
sudo systemctl status legal-case-similarity
```

### Option 3: Docker (Containerized)

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 4: Gunicorn + Uvicorn (Production)

```bash
# Install gunicorn
pip install gunicorn

# Run
gunicorn src.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

## Environment Configuration

Create `.env` file from template:
```bash
cp .env.example .env
# Edit .env with your configuration
```

Key environment variables:
- `HOST`: Server bind address (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `WORKERS`: Number of worker processes (default: auto)
- `LOG_LEVEL`: Logging level (default: warning)
- `RELOAD`: Auto-reload on code changes (default: false)

## Reverse Proxy Setup

### Nginx

```bash
# Install nginx
sudo apt install nginx  # Ubuntu/Debian
sudo dnf install nginx  # CentOS/RHEL

# Configure
sudo nano /etc/nginx/sites-available/legal-case-similarity

# Add configuration (see DEPLOYMENT.md for full config)
# Enable site
sudo ln -s /etc/nginx/sites-available/legal-case-similarity /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Apache

```bash
# Install apache
sudo apt install apache2  # Ubuntu/Debian
sudo dnf install httpd    # CentOS/RHEL

# Enable modules
sudo a2enmod proxy proxy_http headers

# Configure
sudo nano /etc/apache2/sites-available/legal-case-similarity.conf

# Add configuration (see DEPLOYMENT.md for full config)
# Enable site
sudo a2ensite legal-case-similarity
sudo systemctl reload apache2
```

## Health Checks

Verify deployment:
```bash
# Health check
curl http://localhost:8000/api/health

# Performance metrics
curl http://localhost:8000/api/performance

# Test upload (with sample PDF)
curl -X POST -F "file=@sample.pdf" http://localhost:8000/api/upload
```

## Common Issues

### Port Already in Use
```bash
# Linux/macOS
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or change port
export PORT=8001
```

### NLTK Data Missing
```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
```

### Permission Denied
```bash
# Linux
sudo chown -R $USER:$USER /opt/legal-case-similarity
chmod -R 755 /opt/legal-case-similarity
```

### Memory Issues
- Reduce worker count: `export WORKERS=2`
- Increase system memory
- Process documents in smaller batches

## Monitoring

### View Logs
```bash
# Application logs
tail -f logs/app.log
tail -f logs/error.log

# Systemd logs
sudo journalctl -u legal-case-similarity -f

# Docker logs
docker-compose logs -f
```

### Resource Usage
```bash
# CPU and Memory
htop

# Disk usage
df -h

# Network
netstat -tulpn | grep 8000
```

## Security Checklist

- [ ] Update CORS origins in `src/api/main.py`
- [ ] Enable HTTPS with SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Run as non-root user
- [ ] Set appropriate file permissions
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting (if needed)
- [ ] Implement authentication (if needed)
- [ ] Regular security updates

## Performance Optimization

1. **Worker Count**: Set to `(2 × CPU cores) + 1`
2. **Static Files**: Serve via nginx/Apache
3. **Caching**: Enable response caching
4. **Storage**: Use SSD for case repository
5. **Memory**: Allocate 2-4GB for production

## Backup Strategy

Regular backups of:
```bash
# Case repository
tar -czf backup-cases-$(date +%Y%m%d).tar.gz data/cases/

# Metadata
cp data/cases_metadata.json backups/

# Vectors
tar -czf backup-vectors-$(date +%Y%m%d).tar.gz data/vectors/

# Configuration
tar -czf backup-config-$(date +%Y%m%d).tar.gz src/config/ .env
```

## Scaling

### Vertical Scaling
- Increase CPU cores
- Add more RAM
- Use faster storage (SSD/NVMe)

### Horizontal Scaling
- Deploy multiple instances
- Use load balancer (nginx, HAProxy)
- Shared storage for case repository
- Distributed caching (Redis)

## Support

For detailed information:
- **Full Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Production Checklist**: [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)
- **General Documentation**: [README.md](README.md)
- **API Documentation**: http://localhost:8000/docs

## Platform-Specific Notes

### Linux
- Use systemd for service management
- Configure firewall (ufw/firewalld)
- Set up log rotation

### Windows
- Run as Windows Service (optional)
- Configure Windows Defender exceptions
- Use IIS with FastCGI (optional)

### macOS
- Use launchd for service management
- May need Rosetta 2 on Apple Silicon
- Homebrew for dependencies

## Next Steps

1. Review [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)
2. Configure environment variables
3. Set up monitoring and alerting
4. Implement backup strategy
5. Configure SSL/TLS certificates
6. Set up reverse proxy
7. Test deployment thoroughly
8. Document custom configurations

---

**Last Updated**: 2024-01-01
**Version**: 1.0.0
