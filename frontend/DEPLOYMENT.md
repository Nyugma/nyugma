# Frontend Deployment Guide

This guide provides instructions for deploying the Legal Case Similarity frontend to various static hosting platforms.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Netlify Deployment](#netlify-deployment)
- [Vercel Deployment](#vercel-deployment)
- [GitHub Pages Deployment](#github-pages-deployment)
- [Other Static Hosts](#other-static-hosts)
- [Local Testing](#local-testing)
- [Troubleshooting](#troubleshooting)

## Overview

The frontend is a static web application consisting of HTML, CSS, and JavaScript files. It communicates with the backend API via HTTP requests. The backend URL is configured through environment variables during deployment.

### Architecture

```
┌──────────────────────────┐         ┌──────────────────────────┐
│   Frontend (Static)      │         │   Backend (API)          │
│   - Hosted on Netlify/   │  HTTP   │   - Hosted on Render/    │
│     Vercel/GitHub Pages  │◄───────►│     Heroku/etc.          │
│   - HTML/CSS/JS          │ Requests│   - FastAPI REST API     │
└──────────────────────────┘         └──────────────────────────┘
```

### Environment Configuration

The frontend uses a two-tier configuration system:

1. **Development**: Automatically uses `http://localhost:8000` when running on localhost
2. **Production**: Uses `window.ENV.BACKEND_URL` set via the build script

The `build.sh` script generates `js/env.js` from `js/env.js.template` using the `BACKEND_URL` environment variable.

## Prerequisites

Before deploying, ensure you have:

1. **Backend API deployed** and accessible (e.g., on Render)
2. **Backend URL** (e.g., `https://your-api.onrender.com`)
3. **CORS configured** on the backend to allow requests from your frontend domain
4. **Account** on your chosen hosting platform (Netlify, Vercel, or GitHub)

## Netlify Deployment

Netlify is a popular platform for deploying static sites with excellent CI/CD integration.

### Option 1: Deploy via Netlify UI (Recommended for beginners)

1. **Prepare your repository**:
   - Ensure your code is pushed to GitHub, GitLab, or Bitbucket
   - The frontend files should be in the `frontend/` directory

2. **Connect to Netlify**:
   - Go to [netlify.com](https://www.netlify.com/) and sign in
   - Click "Add new site" > "Import an existing project"
   - Choose your Git provider and select your repository

3. **Configure build settings**:
   - **Base directory**: `frontend`
   - **Build command**: `bash build.sh`
   - **Publish directory**: `.` (current directory, since we're already in frontend/)

4. **Set environment variables**:
   - Go to Site settings > Environment variables
   - Add variable:
     - **Key**: `BACKEND_URL`
     - **Value**: `https://your-api.onrender.com` (your backend URL)

5. **Deploy**:
   - Click "Deploy site"
   - Netlify will build and deploy your site
   - You'll get a URL like `https://your-site.netlify.app`

6. **Update backend CORS**:
   - Add your Netlify URL to the backend's `CORS_ORIGINS` environment variable
   - Example: `CORS_ORIGINS=https://your-site.netlify.app`

### Option 2: Deploy via Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Navigate to frontend directory
cd frontend

# Set environment variable
export BACKEND_URL=https://your-api.onrender.com

# Build
bash build.sh

# Deploy
netlify deploy --prod
```

### Option 3: Using netlify.toml Configuration

Create `frontend/netlify.toml`:

```toml
[build]
  base = "frontend"
  command = "bash build.sh"
  publish = "."

[build.environment]
  BACKEND_URL = "https://your-api.onrender.com"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "no-referrer"
    X-XSS-Protection = "1; mode=block"
```

Then push to your repository and Netlify will automatically deploy.

## Vercel Deployment

Vercel is another excellent platform for static site deployment with great performance.

### Option 1: Deploy via Vercel UI

1. **Prepare your repository**:
   - Ensure your code is pushed to GitHub, GitLab, or Bitbucket

2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com/) and sign in
   - Click "Add New" > "Project"
   - Import your repository

3. **Configure project**:
   - **Framework Preset**: Other
   - **Root Directory**: `frontend`
   - **Build Command**: `bash build.sh`
   - **Output Directory**: `.`

4. **Set environment variables**:
   - In the project settings, go to Environment Variables
   - Add variable:
     - **Key**: `BACKEND_URL`
     - **Value**: `https://your-api.onrender.com`
   - Make sure it's set for Production, Preview, and Development

5. **Deploy**:
   - Click "Deploy"
   - You'll get a URL like `https://your-project.vercel.app`

6. **Update backend CORS**:
   - Add your Vercel URL to the backend's `CORS_ORIGINS` environment variable

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Navigate to frontend directory
cd frontend

# Set environment variable
export BACKEND_URL=https://your-api.onrender.com

# Build
bash build.sh

# Deploy
vercel --prod
```

### Option 3: Using vercel.json Configuration

Create `frontend/vercel.json`:

```json
{
  "buildCommand": "bash build.sh",
  "outputDirectory": ".",
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

## GitHub Pages Deployment

GitHub Pages is a free option for hosting static sites directly from your GitHub repository.

### Limitations

- GitHub Pages doesn't support custom build commands with environment variables
- You'll need to manually build and commit the `env.js` file, or use GitHub Actions

### Option 1: Manual Build and Deploy

```bash
# Navigate to frontend directory
cd frontend

# Set environment variable and build
export BACKEND_URL=https://your-api.onrender.com
bash build.sh

# Commit the generated env.js
git add js/env.js
git commit -m "Add production environment configuration"
git push

# Enable GitHub Pages in repository settings
# Settings > Pages > Source: Deploy from a branch
# Branch: main, Folder: /frontend
```

### Option 2: Using GitHub Actions

Create `.github/workflows/deploy-frontend.yml`:

```yaml
name: Deploy Frontend to GitHub Pages

on:
  push:
    branches: [ main ]
    paths:
      - 'frontend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build frontend
        env:
          BACKEND_URL: ${{ secrets.BACKEND_URL }}
        run: |
          cd frontend
          bash build.sh
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./frontend
          publish_branch: gh-pages
```

Then add `BACKEND_URL` as a repository secret in Settings > Secrets and variables > Actions.

## Other Static Hosts

The frontend can be deployed to any static hosting service. Here are general instructions:

### General Deployment Steps

1. **Build the frontend**:
   ```bash
   cd frontend
   export BACKEND_URL=https://your-api.onrender.com
   bash build.sh
   ```

2. **Upload files**:
   - Upload all files in the `frontend/` directory to your hosting service
   - Ensure `js/env.js` is included (generated by build.sh)

3. **Configure routing** (if supported):
   - Set up redirects so all routes serve `index.html` (for SPA routing)

4. **Update backend CORS**:
   - Add your frontend domain to the backend's `CORS_ORIGINS` environment variable

### Supported Platforms

- **AWS S3 + CloudFront**: Use S3 for storage and CloudFront for CDN
- **Google Cloud Storage**: Host static files with Cloud Storage
- **Azure Static Web Apps**: Microsoft's static hosting service
- **Cloudflare Pages**: Fast global CDN with automatic deployments
- **Surge.sh**: Simple CLI-based deployment
- **Firebase Hosting**: Google's hosting platform with CLI tools

## Local Testing

### Test Production Build Locally

To test the production build before deploying:

```bash
# Navigate to frontend directory
cd frontend

# Set backend URL to your deployed backend (or localhost for testing)
export BACKEND_URL=https://your-api.onrender.com

# Run build script
bash build.sh

# Serve the frontend locally
# Option 1: Python
python -m http.server 8080

# Option 2: Node.js
npx http-server -p 8080

# Option 3: PHP
php -S localhost:8080
```

Then open `http://localhost:8080` in your browser.

### Test with Local Backend

```bash
# Set backend URL to localhost
export BACKEND_URL=http://localhost:8000

# Run build script
bash build.sh

# Serve frontend
python -m http.server 8080
```

**Note**: For local development, you don't need to run the build script. The frontend automatically detects localhost and uses `http://localhost:8000`.

## Troubleshooting

### Issue: "Failed to fetch" or CORS errors

**Symptoms**: Browser console shows CORS errors or "Failed to fetch" messages.

**Solutions**:
1. **Check backend CORS configuration**:
   - Ensure `CORS_ORIGINS` environment variable includes your frontend domain
   - Example: `CORS_ORIGINS=https://your-site.netlify.app,https://your-site.vercel.app`

2. **Check backend URL**:
   - Verify `BACKEND_URL` is set correctly in your deployment platform
   - Check `js/env.js` contains the correct URL
   - Test the backend URL directly in your browser (should return JSON)

3. **Check backend is running**:
   - Visit your backend URL (e.g., `https://your-api.onrender.com`)
   - Should return JSON with API information
   - Check backend logs for errors

### Issue: env.js not found or contains template variables

**Symptoms**: Frontend uses default URL or shows `${BACKEND_URL}` in requests.

**Solutions**:
1. **Verify build script ran**:
   - Check deployment logs for "Successfully generated js/env.js"
   - Verify `BACKEND_URL` environment variable was set

2. **Check file was deployed**:
   - Verify `js/env.js` exists in deployed files
   - Check it doesn't contain `${BACKEND_URL}` placeholder

3. **Rebuild and redeploy**:
   ```bash
   cd frontend
   export BACKEND_URL=https://your-api.onrender.com
   bash build.sh
   # Then redeploy
   ```

### Issue: Build script fails

**Symptoms**: Deployment fails with error from build.sh.

**Solutions**:
1. **Check bash is available**:
   - Most platforms support bash
   - If not, you may need to use a different shell or manual build

2. **Check template file exists**:
   - Verify `js/env.js.template` is in your repository
   - Check it's in the correct location (`frontend/js/env.js.template`)

3. **Check environment variable**:
   - Verify `BACKEND_URL` is set in your deployment platform
   - Check for typos in the variable name

### Issue: Frontend loads but can't connect to backend

**Symptoms**: Frontend displays but API requests fail.

**Solutions**:
1. **Check network tab**:
   - Open browser DevTools > Network tab
   - Look at the URL being requested
   - Verify it matches your backend URL

2. **Test backend directly**:
   - Visit backend URL in browser
   - Should return JSON response
   - If not, backend may be down or misconfigured

3. **Check HTTPS/HTTP mismatch**:
   - If frontend is HTTPS, backend must be HTTPS
   - Mixed content (HTTPS → HTTP) is blocked by browsers

### Issue: 404 errors on page refresh

**Symptoms**: Direct navigation to `/search.html` works, but refresh gives 404.

**Solutions**:
1. **Configure redirects** (for SPA routing):
   - Netlify: Add redirects in `netlify.toml`
   - Vercel: Automatically handled
   - GitHub Pages: May need custom 404.html

2. **Use hash routing**:
   - Alternative: Use `#/search` instead of `/search.html`
   - Requires JavaScript routing changes

### Getting Help

If you encounter issues not covered here:

1. **Check browser console**: Look for error messages
2. **Check network tab**: Inspect failed requests
3. **Check backend logs**: Look for CORS or request errors
4. **Check deployment logs**: Look for build failures
5. **Test locally**: Verify it works with local backend first

For more help:
- Backend API documentation: Visit your backend URL (e.g., `https://your-api.onrender.com`)
- Interactive API docs: Visit `https://your-api.onrender.com/docs`
- Repository issues: Check the GitHub repository for known issues

## Security Considerations

### Environment Variables

- Never commit `js/env.js` to version control (it's in `.gitignore`)
- Always use environment variables in your deployment platform
- Rotate backend URLs if they become compromised

### HTTPS

- Always use HTTPS for production deployments
- Most platforms (Netlify, Vercel) provide free SSL certificates
- Ensure backend also uses HTTPS

### CORS

- Configure CORS to only allow your specific frontend domains
- Don't use `CORS_ORIGINS=*` in production
- Update CORS when you change frontend domains

### Headers

- Use security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- Most platforms support custom headers via configuration files
- See netlify.toml and vercel.json examples above

## Next Steps

After successful deployment:

1. **Test all functionality**:
   - Upload a PDF file
   - Verify search results display
   - Test case download
   - Test on different browsers and devices

2. **Monitor performance**:
   - Check page load times
   - Monitor API response times
   - Use browser DevTools Performance tab

3. **Set up monitoring**:
   - Use platform analytics (Netlify Analytics, Vercel Analytics)
   - Set up error tracking (Sentry, LogRocket, etc.)
   - Monitor backend health endpoint

4. **Configure custom domain** (optional):
   - Most platforms support custom domains
   - Follow platform-specific instructions
   - Update backend CORS with new domain

5. **Set up CI/CD**:
   - Configure automatic deployments on git push
   - Set up preview deployments for pull requests
   - Add deployment status badges to README

## Additional Resources

- [Netlify Documentation](https://docs.netlify.com/)
- [Vercel Documentation](https://vercel.com/docs)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [MDN: CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Backend Deployment Guide](../DEPLOYMENT.md)
