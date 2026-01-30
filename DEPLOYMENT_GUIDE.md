# Deployment Guide

This guide explains how to deploy the Legal Case Similarity application with its separated frontend and backend architecture.

## Overview

The application consists of two independent components:

1. **Frontend** - Static HTML/CSS/JavaScript files (deploy on Netlify, Vercel, GitHub Pages, etc.)
2. **Backend** - Python FastAPI application (deploy on Render, Heroku, Railway, etc.)

## Quick Deployment Steps

### Step 1: Deploy Backend First

1. **Choose a platform** (Render recommended)
2. **Deploy the `backend/` folder**
3. **Note the backend URL** (e.g., `https://your-api.onrender.com`)

### Step 2: Deploy Frontend

1. **Choose a platform** (Netlify recommended)
2. **Configure backend URL** in environment variables
3. **Deploy the `frontend/` folder**

### Step 3: Configure CORS

Update backend environment variables to allow frontend domain:
```bash
CORS_ORIGINS=https://your-frontend.netlify.app
```

## Detailed Deployment Instructions

### Backend Deployment on Render

1. **Sign up at [render.com](https://render.com)**

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository

3. **Configure Service**
   ```
   Name: legal-case-api
   Region: Choose closest to your users
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   ```

4. **Build & Start Commands**
   ```bash
   # Build Command
   pip install -r requirements.txt && python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
   
   # Start Command
   python uvicorn_production.py
   ```

5. **Environment Variables**
   ```bash
   HOST=0.0.0.0
   PORT=8000
   WORKERS=4
   LOG_LEVEL=warning
   CORS_ORIGINS=*  # Update after frontend deployment
   ```

6. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Note your backend URL: `https://your-api.onrender.com`

7. **Test Backend**
   ```bash
   curl https://your-api.onrender.com/api/health
   ```

### Frontend Deployment on Netlify

1. **Sign up at [netlify.com](https://netlify.com)**

2. **Create New Site**
   - Click "Add new site" → "Import an existing project"
   - Connect your GitHub repository
   - Select the repository

3. **Configure Build Settings**
   ```
   Base directory: frontend
   Build command: (leave empty)
   Publish directory: .
   ```

4. **Environment Variables**
   - Go to Site settings → Environment variables
   - Add variable:
     ```
     Key: BACKEND_URL
     Value: https://your-api.onrender.com
     ```

5. **Optional: Custom Build Script**
   
   If you want to inject the backend URL at build time:
   
   a. Update build command to: `bash build.sh`
   
   b. The `build.sh` script will create `js/env.js` with:
   ```javascript
   window.ENV = { BACKEND_URL: 'https://your-api.onrender.com' };
   ```

6. **Deploy**
   - Click "Deploy site"
   - Wait for deployment to complete
   - Note your frontend URL: `https://your-site.netlify.app`

7. **Test Frontend**
   - Open `https://your-site.netlify.app` in browser
   - Try uploading a PDF file

### Update Backend CORS

After frontend deployment, update backend environment variables:

1. Go to Render dashboard → Your service → Environment
2. Update `CORS_ORIGINS`:
   ```bash
   CORS_ORIGINS=https://your-site.netlify.app
   ```
3. Save changes (service will automatically redeploy)

## Alternative Deployment Options

### Frontend Alternatives

#### Vercel

```bash
cd frontend
npm i -g vercel
vercel
# Follow prompts
# Set BACKEND_URL environment variable in Vercel dashboard
```

#### GitHub Pages

1. Go to repository Settings → Pages
2. Select branch and `/frontend` folder
3. Update `frontend/js/config.js` with backend URL:
   ```javascript
   return 'https://your-api.onrender.com';
   ```

### Backend Alternatives

#### Heroku

1. Create `Procfile` in backend folder:
   ```
   web: python uvicorn_production.py
   ```

2. Deploy:
   ```bash
   cd backend
   heroku create your-app-name
   git subtree push --prefix backend heroku main
   ```

3. Set environment variables:
   ```bash
   heroku config:set CORS_ORIGINS=https://your-frontend.com
   ```

#### Railway

1. Create new project on [railway.app](https://railway.app)
2. Connect GitHub repository
3. Set root directory to `backend`
4. Railway auto-detects Python and uses `requirements.txt`
5. Add environment variables in Railway dashboard

#### Docker (Self-hosted)

```bash
cd backend
docker build -t legal-case-api .
docker run -p 8000:8000 \
  -e CORS_ORIGINS=https://your-frontend.com \
  legal-case-api
```

Or use docker-compose:
```bash
cd backend
docker-compose up -d
```

## Environment Variables Reference

### Backend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HOST` | No | `0.0.0.0` | Server host address |
| `PORT` | No | `8000` | Server port |
| `WORKERS` | No | `4` | Number of worker processes |
| `LOG_LEVEL` | No | `info` | Logging level (debug/info/warning/error) |
| `CORS_ORIGINS` | Yes | `*` | Comma-separated list of allowed origins |
| `FRONTEND_URL` | No | - | Frontend URL for API info |

### Frontend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BACKEND_URL` | Yes | - | Backend API URL |

## Configuration Examples

### Development Configuration

**Backend (.env):**
```bash
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=debug
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
FRONTEND_URL=http://localhost:3000
```

**Frontend:**
- No configuration needed (auto-detects localhost)

### Production Configuration

**Backend (Render):**
```bash
HOST=0.0.0.0
PORT=8000
WORKERS=4
LOG_LEVEL=warning
CORS_ORIGINS=https://your-frontend.netlify.app
FRONTEND_URL=https://your-frontend.netlify.app
```

**Frontend (Netlify):**
```bash
BACKEND_URL=https://your-api.onrender.com
```

## Troubleshooting

### CORS Errors

**Symptom:** Browser console shows CORS policy errors

**Solution:**
1. Check backend `CORS_ORIGINS` includes your frontend URL
2. Ensure no trailing slashes in URLs
3. Verify backend is running: `curl https://your-api.com/api/health`
4. Check browser network tab for actual error

### Frontend Can't Connect to Backend

**Symptom:** "Failed to fetch" or "Network error"

**Solution:**
1. Verify backend URL in frontend config
2. Check backend is accessible: `curl https://your-api.com/api/health`
3. Check browser console for specific error
4. Verify CORS is configured correctly

### Backend Build Fails

**Symptom:** Deployment fails during build

**Solution:**
1. Check Python version (must be 3.8+)
2. Verify `requirements.txt` is correct
3. Check build logs for specific error
4. Ensure NLTK download command is in build script

### File Upload Fails

**Symptom:** Upload returns error or times out

**Solution:**
1. Check file size (must be under limit)
2. Verify file is valid PDF
3. Check backend logs for errors
4. Ensure sufficient disk space on server

## Monitoring & Maintenance

### Health Checks

Both platforms support health checks:

**Render:**
- Automatically uses `/api/health` endpoint
- Configure in service settings

**Netlify:**
- No health checks needed (static files)

### Logs

**Backend Logs:**
- Render: View in dashboard → Logs tab
- Heroku: `heroku logs --tail`
- Docker: `docker logs container-name`

**Frontend Logs:**
- Check browser console for client-side errors
- Netlify: View deploy logs in dashboard

### Scaling

**Backend:**
- Render: Upgrade plan for more resources
- Heroku: Scale dynos: `heroku ps:scale web=2`
- Docker: Increase worker count in environment variables

**Frontend:**
- Static files scale automatically on CDN
- No configuration needed

## Security Checklist

Before going to production:

- [ ] Update `CORS_ORIGINS` to specific domains (remove `*`)
- [ ] Set `LOG_LEVEL` to `warning` or `error`
- [ ] Enable HTTPS on both frontend and backend
- [ ] Review file upload size limits
- [ ] Set up monitoring and alerts
- [ ] Configure backup strategy for data files
- [ ] Review and update dependencies
- [ ] Set up rate limiting (if needed)
- [ ] Configure proper error pages

## Cost Estimates

### Free Tier Options

**Backend:**
- Render: Free tier available (sleeps after inactivity)
- Heroku: Free tier discontinued (paid plans start at $7/month)
- Railway: $5 free credit per month

**Frontend:**
- Netlify: 100GB bandwidth/month free
- Vercel: 100GB bandwidth/month free
- GitHub Pages: Free for public repositories

### Recommended Production Setup

- **Backend**: Render Starter ($7/month) or Railway ($5-10/month)
- **Frontend**: Netlify/Vercel free tier (sufficient for most use cases)
- **Total**: ~$7-10/month

## Support

For deployment issues:

1. Check platform-specific documentation:
   - [Render Docs](https://render.com/docs)
   - [Netlify Docs](https://docs.netlify.com)
   - [Vercel Docs](https://vercel.com/docs)

2. Review application logs for errors

3. Check [backend/README.md](backend/README.md) and [frontend/README.md](frontend/README.md) for detailed instructions

4. Open an issue on GitHub with:
   - Platform being used
   - Error messages
   - Configuration used
   - Steps to reproduce
