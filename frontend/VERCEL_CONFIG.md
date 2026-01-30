# Vercel Configuration Documentation

This document explains the `vercel.json` configuration file for deploying the Legal Case Similarity Frontend on Vercel.

## Overview

The `vercel.json` file configures how Vercel builds and deploys the frontend application. Since JSON doesn't support comments, this document provides detailed explanations of each configuration option.

## Configuration Reference

### Build Configuration

```json
"buildCommand": "bash build.sh"
```
- **Purpose**: Command to run during the build process
- **What it does**: Executes the `build.sh` script which generates `js/env.js` with the backend URL from environment variables
- **When it runs**: Once during deployment, before the site goes live

```json
"outputDirectory": "."
```
- **Purpose**: Specifies which directory to deploy
- **Value**: `.` means deploy the current directory (frontend/)
- **Note**: All files in the frontend directory will be served as static assets

### Environment Variables

```json
"env": {
  "BACKEND_URL": "https://your-api.onrender.com"
}
```
- **Purpose**: Sets environment variables available during build time
- **BACKEND_URL**: The URL of your deployed backend API
- **Important**: Replace `https://your-api.onrender.com` with your actual backend URL
- **Alternative**: You can also set this in the Vercel dashboard under Project Settings > Environment Variables

### Security Headers

The configuration sets several security headers to protect against common web vulnerabilities:

#### X-Frame-Options: DENY
```json
{
  "key": "X-Frame-Options",
  "value": "DENY"
}
```
- **Purpose**: Prevents clickjacking attacks
- **Effect**: Prevents the site from being embedded in iframes
- **Security**: Protects users from being tricked into clicking on hidden elements

#### X-Content-Type-Options: nosniff
```json
{
  "key": "X-Content-Type-Options",
  "value": "nosniff"
}
```
- **Purpose**: Prevents MIME type sniffing
- **Effect**: Forces browsers to respect the declared content type
- **Security**: Prevents browsers from interpreting files as a different MIME type

#### Referrer-Policy: no-referrer
```json
{
  "key": "Referrer-Policy",
  "value": "no-referrer"
}
```
- **Purpose**: Controls referrer information sent with requests
- **Effect**: No referrer information is sent with requests
- **Privacy**: Protects user privacy by not leaking the referring page URL

#### X-XSS-Protection: 1; mode=block
```json
{
  "key": "X-XSS-Protection",
  "value": "1; mode=block"
}
```
- **Purpose**: Enables XSS (Cross-Site Scripting) protection in older browsers
- **Effect**: Blocks pages when XSS attacks are detected
- **Note**: Modern browsers use Content Security Policy instead, but this provides backward compatibility

### Cache Control Headers

The configuration sets different cache policies for different types of files:

#### Static Assets (CSS, JS, Images)
```json
{
  "source": "/css/(.*)",
  "headers": [
    {
      "key": "Cache-Control",
      "value": "public, max-age=31536000, immutable"
    }
  ]
}
```
- **Purpose**: Aggressive caching for static assets
- **max-age=31536000**: Cache for 1 year (31,536,000 seconds)
- **immutable**: Tells browsers the file will never change
- **Performance**: Significantly improves load times for returning visitors
- **Applies to**: `/css/*`, `/js/*`, `/assets/*`

#### HTML Files
```json
{
  "source": "/(.*).html",
  "headers": [
    {
      "key": "Cache-Control",
      "value": "public, max-age=0, must-revalidate"
    }
  ]
}
```
- **Purpose**: Prevents caching of HTML files
- **max-age=0**: Don't cache
- **must-revalidate**: Always check with server for updates
- **Reason**: Ensures users always get the latest version of the application

### URL Rewrites

```json
"rewrites": [
  {
    "source": "/(.*)",
    "destination": "/index.html"
  }
]
```
- **Purpose**: Enables client-side routing
- **Effect**: All requests are served with `index.html`
- **Benefit**: Direct navigation to `/search.html` works correctly
- **Note**: The frontend JavaScript handles routing to the correct page

## Deployment Steps

### 1. Prerequisites
- Vercel account (free tier available)
- Backend API deployed and accessible
- Git repository with your code

### 2. Deploy to Vercel

#### Option A: Using Vercel CLI
```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend directory
cd frontend

# Deploy
vercel

# Follow the prompts to configure your project
```

#### Option B: Using Vercel Dashboard
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your Git repository
4. Set the root directory to `frontend`
5. Vercel will automatically detect `vercel.json`
6. Click "Deploy"

### 3. Configure Environment Variables

After deployment, update the environment variable:

1. Go to your project in Vercel dashboard
2. Navigate to Settings > Environment Variables
3. Add `BACKEND_URL` with your actual backend URL
4. Example: `https://legal-case-similarity-api.onrender.com`
5. Redeploy the project for changes to take effect

### 4. Verify Deployment

1. Visit your deployed site URL (e.g., `https://your-project.vercel.app`)
2. Check that the home page loads correctly
3. Navigate to the search page
4. Test file upload functionality
5. Verify API calls reach your backend

## Troubleshooting

### Build Fails
- **Issue**: `build.sh` script fails
- **Solution**: Ensure `build.sh` has execute permissions and uses Unix line endings (LF, not CRLF)
- **Check**: Run `bash build.sh` locally to test

### API Calls Fail
- **Issue**: Frontend can't connect to backend
- **Solution**: 
  1. Verify `BACKEND_URL` is set correctly in environment variables
  2. Check that backend CORS is configured to allow your Vercel domain
  3. Ensure backend is running and accessible

### 404 Errors on Direct Navigation
- **Issue**: Navigating directly to `/search.html` returns 404
- **Solution**: Verify the `rewrites` configuration is present in `vercel.json`
- **Note**: This should be handled automatically by the configuration

### Security Headers Not Applied
- **Issue**: Security headers don't appear in browser dev tools
- **Solution**: 
  1. Clear browser cache
  2. Verify deployment completed successfully
  3. Check Vercel deployment logs for errors

## Advanced Configuration

### Custom Domain

To use a custom domain:

1. Go to Project Settings > Domains
2. Add your domain
3. Configure DNS records as instructed by Vercel
4. Update backend CORS to include your custom domain

### Multiple Environments

To set up staging and production environments:

1. Create separate environment variables for each environment
2. Use Vercel's environment-specific variables:
   - Production: Used for production deployments
   - Preview: Used for preview deployments (PRs)
   - Development: Used for local development

Example:
```json
"env": {
  "BACKEND_URL": "https://api-production.onrender.com"
},
"build": {
  "env": {
    "BACKEND_URL": "https://api-staging.onrender.com"
  }
}
```

### Content Security Policy

For enhanced security, you can add a Content Security Policy header:

```json
{
  "key": "Content-Security-Policy",
  "value": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://your-api.onrender.com"
}
```

**Note**: Adjust the policy based on your specific needs. The `'unsafe-inline'` values are needed for inline scripts and styles.

## Resources

- [Vercel Documentation](https://vercel.com/docs)
- [vercel.json Reference](https://vercel.com/docs/project-configuration)
- [Environment Variables](https://vercel.com/docs/environment-variables)
- [Custom Domains](https://vercel.com/docs/custom-domains)
- [Security Headers](https://vercel.com/docs/edge-network/headers)

## Support

For issues specific to this application:
- Check the main README.md in the repository root
- Review the frontend/README.md for frontend-specific documentation
- Check backend logs for API-related issues

For Vercel-specific issues:
- Visit [Vercel Support](https://vercel.com/support)
- Check [Vercel Community](https://github.com/vercel/vercel/discussions)
