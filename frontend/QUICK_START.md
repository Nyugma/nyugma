# Frontend Quick Start Guide

Quick reference for deploying the Legal Case Similarity frontend.

## Prerequisites

✅ Backend API deployed and accessible  
✅ Backend URL (e.g., `https://your-api.onrender.com`)  
✅ Backend CORS configured to allow your frontend domain

## Local Development

No build step needed! Just serve the files:

```bash
cd frontend

# Option 1: Python
python -m http.server 8080

# Option 2: Node.js
npx http-server -p 8080

# Option 3: PHP
php -S localhost:8080
```

Then open `http://localhost:8080` in your browser.

The frontend automatically uses `http://localhost:8000` for the backend when running on localhost.

## Production Deployment

### Step 1: Choose Your Platform

- **Netlify** (Recommended) - Easy UI, automatic deployments
- **Vercel** - Great performance, automatic deployments
- **GitHub Pages** - Free, requires manual build or GitHub Actions
- **Other** - Any static hosting service

### Step 2: Set Environment Variable

In your deployment platform, set:

- **Variable Name**: `BACKEND_URL`
- **Variable Value**: `https://your-api.onrender.com` (your actual backend URL)

### Step 3: Configure Build Command

Set the build command to:

- **Linux/Mac**: `bash build.sh`
- **Windows**: `powershell -ExecutionPolicy Bypass -File build.ps1`

Most platforms (Netlify, Vercel) support bash by default.

### Step 4: Deploy

Push your code or click deploy. The platform will:

1. Run the build script
2. Generate `js/env.js` with your backend URL
3. Deploy the static files

### Step 5: Update Backend CORS

Add your frontend URL to the backend's `CORS_ORIGINS` environment variable:

```bash
CORS_ORIGINS=https://your-site.netlify.app,https://your-site.vercel.app
```

## Platform-Specific Instructions

### Netlify

1. Connect your repository
2. Set base directory: `frontend`
3. Set build command: `bash build.sh`
4. Set publish directory: `.`
5. Add environment variable: `BACKEND_URL=https://your-api.onrender.com`
6. Deploy!

### Vercel

1. Import your repository
2. Set root directory: `frontend`
3. Set build command: `bash build.sh`
4. Set output directory: `.`
5. Add environment variable: `BACKEND_URL=https://your-api.onrender.com`
6. Deploy!

### GitHub Pages

**Option A: Manual Build**
```bash
cd frontend
export BACKEND_URL=https://your-api.onrender.com
bash build.sh
git add js/env.js
git commit -m "Add production config"
git push
```

**Option B: GitHub Actions**

See [DEPLOYMENT.md](DEPLOYMENT.md#github-pages-deployment) for workflow setup.

## Testing Your Deployment

1. **Visit your frontend URL** (e.g., `https://your-site.netlify.app`)
2. **Open browser DevTools** (F12)
3. **Check Console** for errors
4. **Check Network tab** to see API requests
5. **Upload a test PDF** to verify functionality

## Troubleshooting

### ❌ CORS Errors

**Problem**: Browser console shows CORS errors

**Solution**: Add your frontend domain to backend's `CORS_ORIGINS`:
```bash
CORS_ORIGINS=https://your-site.netlify.app
```

### ❌ Wrong Backend URL

**Problem**: Requests go to wrong URL or show `${BACKEND_URL}`

**Solution**: 
1. Check `BACKEND_URL` is set in deployment platform
2. Check build logs show "Successfully generated js/env.js"
3. Verify `js/env.js` exists in deployed files

### ❌ Build Fails

**Problem**: Deployment fails during build

**Solution**:
1. Check build logs for error messages
2. Verify `js/env.js.template` exists in repository
3. Verify build command is correct for your platform

### ❌ 404 on Page Refresh

**Problem**: Direct navigation works, but refresh gives 404

**Solution**: Configure redirects (see [DEPLOYMENT.md](DEPLOYMENT.md))

## Configuration Files

The repository includes configuration files for popular platforms:

- **netlify.toml** - Netlify configuration
- **vercel.json** - Vercel configuration
- **build.sh** - Linux/Mac build script
- **build.ps1** - Windows PowerShell build script

These files are pre-configured and ready to use!

## Need More Help?

- **Detailed Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **JavaScript Docs**: See [js/README.md](js/README.md)
- **Backend Setup**: See [../README.md](../README.md)
- **API Docs**: Visit your backend URL (e.g., `https://your-api.onrender.com/docs`)

## Quick Commands Reference

```bash
# Local development
cd frontend && python -m http.server 8080

# Manual build (Linux/Mac)
cd frontend && export BACKEND_URL=https://your-api.onrender.com && bash build.sh

# Manual build (Windows)
cd frontend
$env:BACKEND_URL="https://your-api.onrender.com"
.\build.ps1

# Test generated config
cat js/env.js

# Clean generated files
rm js/env.js
```

## Security Checklist

- [ ] Backend uses HTTPS (not HTTP)
- [ ] CORS configured with specific domains (not `*`)
- [ ] `env.js` is in `.gitignore` (not committed)
- [ ] Environment variables set in deployment platform (not hardcoded)
- [ ] Security headers configured (see netlify.toml/vercel.json)

## Success Criteria

✅ Frontend loads without errors  
✅ Can upload PDF files  
✅ Search results display correctly  
✅ Can download case files  
✅ Works on mobile and desktop  
✅ No CORS errors in console  
✅ HTTPS enabled  

---

**Ready to deploy?** Follow the steps above or see [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.
