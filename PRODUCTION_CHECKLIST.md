# Production Deployment Checklist

This checklist ensures all necessary steps are completed before deploying the Legal Case Similarity Web Application to production.

## Pre-Deployment Checklist

### 1. Environment Setup
- [ ] Python 3.8+ installed on target system
- [ ] Virtual environment created and activated
- [ ] All dependencies installed from requirements.txt
- [ ] NLTK data downloaded (stopwords, punkt, wordnet)
- [ ] Verify installation with `python verify_setup.py`

### 2. Configuration
- [ ] Update CORS origins in `src/api/main.py` to production domains
- [ ] Set environment variables for production:
  - [ ] `HOST=0.0.0.0`
  - [ ] `PORT=8000` (or custom port)
  - [ ] `RELOAD=false`
  - [ ] `LOG_LEVEL=warning` or `error`
  - [ ] `WORKERS=<optimal_count>`
- [ ] Configure logging paths in `src/config/logging_config.py`
- [ ] Review and update `src/config/settings.py` for production

### 3. Data Preparation
- [ ] Legal vocabulary file exists at `data/legal_vocabulary.json`
- [ ] Case repository populated in `data/cases/`
- [ ] Case metadata file exists at `data/cases_metadata.json`
- [ ] Pre-computed vectors available in `data/vectors/`
- [ ] Vectorizer model trained and saved
- [ ] Verify data consistency with health check endpoint

### 4. Security Configuration
- [ ] CORS origins restricted to specific domains (not "*")
- [ ] File upload size limits configured (default: 10MB)
- [ ] HTTPS/SSL certificates configured (if applicable)
- [ ] Firewall rules configured to allow only necessary ports
- [ ] Application runs as non-root user
- [ ] Sensitive configuration moved to environment variables
- [ ] Rate limiting implemented (if required)
- [ ] Authentication configured (if handling sensitive data)

### 5. Performance Optimization
- [ ] Worker count optimized for available CPU cores
- [ ] Memory limits configured appropriately
- [ ] Static file serving configured (nginx/Apache)
- [ ] Response caching enabled (if applicable)
- [ ] Database/storage optimized for production load
- [ ] Connection pooling configured

### 6. Monitoring and Logging
- [ ] Application logs directory created (`logs/`)
- [ ] Log rotation configured (logrotate)
- [ ] Health check endpoint accessible (`/api/health`)
- [ ] Performance monitoring endpoint accessible (`/api/performance`)
- [ ] Error tracking configured
- [ ] Uptime monitoring configured
- [ ] Resource usage monitoring configured

### 7. Backup and Recovery
- [ ] Backup strategy defined for:
  - [ ] Case repository (`data/cases/`)
  - [ ] Metadata (`data/cases_metadata.json`)
  - [ ] Vectors (`data/vectors/`)
  - [ ] Configuration files
- [ ] Backup schedule configured
- [ ] Recovery procedure documented and tested
- [ ] Disaster recovery plan in place

### 8. Testing
- [ ] All unit tests passing (`pytest tests/unit/`)
- [ ] All property-based tests passing (`pytest tests/property/`)
- [ ] Integration tests completed
- [ ] Load testing performed
- [ ] Security testing completed
- [ ] Cross-platform compatibility verified

### 9. Documentation
- [ ] README.md updated with production instructions
- [ ] DEPLOYMENT.md reviewed and accurate
- [ ] API documentation accessible
- [ ] Troubleshooting guide available
- [ ] Runbook created for operations team

### 10. Deployment Method
Choose and configure one deployment method:

#### Option A: Systemd Service (Linux)
- [ ] Service file created at `/etc/systemd/system/legal-case-similarity.service`
- [ ] Service enabled: `sudo systemctl enable legal-case-similarity`
- [ ] Service starts on boot
- [ ] Service restart policy configured

#### Option B: Docker
- [ ] Dockerfile created and tested
- [ ] docker-compose.yml configured
- [ ] Container builds successfully
- [ ] Volumes configured for persistent data
- [ ] Container orchestration configured (if applicable)

#### Option C: Reverse Proxy
- [ ] Nginx or Apache configured
- [ ] Proxy headers configured
- [ ] Static file serving configured
- [ ] SSL/TLS termination configured
- [ ] Load balancing configured (if applicable)

### 11. Post-Deployment Verification
- [ ] Application starts without errors
- [ ] Health check endpoint returns healthy status
- [ ] Upload endpoint accepts and processes PDFs
- [ ] Search results returned correctly
- [ ] Frontend interface loads and functions
- [ ] API documentation accessible
- [ ] Logs being written correctly
- [ ] Performance metrics within acceptable range
- [ ] No memory leaks detected
- [ ] Error handling working as expected

### 12. Rollback Plan
- [ ] Previous version backed up
- [ ] Rollback procedure documented
- [ ] Rollback tested in staging environment
- [ ] Database migration rollback plan (if applicable)

## Production Startup Commands

### Development Mode (Testing)
```bash
python run_api.py
```

### Production Mode (Direct)
```bash
python uvicorn_production.py
```

### Production Mode (Systemd)
```bash
sudo systemctl start legal-case-similarity
sudo systemctl status legal-case-similarity
```

### Production Mode (Docker)
```bash
docker-compose up -d
docker-compose logs -f
```

### Production Mode (Gunicorn + Uvicorn)
```bash
gunicorn src.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

## Monitoring Commands

### Check Application Health
```bash
curl http://localhost:8000/api/health
```

### Check Performance Metrics
```bash
curl http://localhost:8000/api/performance
```

### View Application Logs
```bash
tail -f logs/app.log
tail -f logs/error.log
```

### View System Logs (Systemd)
```bash
sudo journalctl -u legal-case-similarity -f
```

### Monitor Resource Usage
```bash
# CPU and Memory
htop

# Disk Usage
df -h

# Network Connections
netstat -tulpn | grep 8000
```

## Emergency Procedures

### Application Not Responding
1. Check if process is running
2. Review error logs
3. Check system resources (CPU, memory, disk)
4. Restart application
5. If issue persists, rollback to previous version

### High Memory Usage
1. Check for memory leaks in logs
2. Reduce worker count
3. Restart application
4. Monitor memory usage over time
5. Consider scaling horizontally

### High CPU Usage
1. Check for infinite loops or blocking operations
2. Review recent code changes
3. Reduce worker count temporarily
4. Enable performance profiling
5. Optimize identified bottlenecks

### Database/Storage Issues
1. Check disk space availability
2. Verify file permissions
3. Check for corrupted files
4. Restore from backup if necessary
5. Rebuild indexes if applicable

## Support Contacts

- **Technical Lead**: [Contact Information]
- **DevOps Team**: [Contact Information]
- **On-Call Engineer**: [Contact Information]
- **Documentation**: See README.md and DEPLOYMENT.md

## Sign-Off

- [ ] Deployment reviewed by: _________________ Date: _______
- [ ] Security reviewed by: _________________ Date: _______
- [ ] Operations approved by: _________________ Date: _______
- [ ] Production deployment authorized by: _________________ Date: _______

---

**Last Updated**: 2024-01-01
**Version**: 1.0.0
