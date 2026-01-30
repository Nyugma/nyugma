# Legal Case Similarity - Frontend

Static web application for the Legal Case Similarity search system. This frontend communicates with the backend API to provide a user-friendly interface for uploading legal documents and finding similar cases.

## Overview

The frontend is a standalone static web application that can be deployed independently from the backend API. It consists of HTML, CSS, and JavaScript files that run entirely in the browser.

### Architecture

```
┌──────────────────────────┐         ┌──────────────────────────┐
│   Frontend (Static)      │         │   Backend (API)          │
│   - HTML/CSS/JavaScript  │  HTTP   │   - FastAPI REST API     │
│   - Hosted separately    │◄───────►│   - Hosted on Render     │
│   - Configurable API URL │ Requests│   - CORS enabled         │
└──────────────────────────┘         └──────────────────────────┘
```

## Quick Start

### Local Development

No build step required for local development:

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

The frontend automatically detects localhost and uses `http://localhost:8000` as the backend URL.

### Production Deployment

See [QUICK_START.md](QUICK_START.md) for a quick deployment guide, or [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive instructions.

**TL;DR**:
1. Set `BACKEND_URL` environment variable in your deployment platform
2. Set build command to `bash build.sh`
3. Deploy to Netlify, Vercel, or any static hosting service
4. Update backend CORS to allow your frontend domain

## Directory Structure

```
frontend/
├── index.html              # Home/landing page (coming soon)
├── search.html             # Search interface
├── css/
│   └── styles.css          # Application styles
├── js/
│   ├── app.js              # Main application logic
│   ├── config.js           # Configuration module
│   ├── env.js.template     # Environment template (for build)
│   └── README.md           # JavaScript documentation
├── assets/                 # Images and other assets
├── build.sh                # Build script (Linux/Mac)
├── build.ps1               # Build script (Windows)
├── netlify.toml            # Netlify configuration
├── vercel.json             # Vercel configuration
├── README.md               # This file
├── QUICK_START.md          # Quick deployment guide
└── DEPLOYMENT.md           # Comprehensive deployment guide
```

## Features

- **PDF Upload**: Upload legal documents for similarity analysis
- **Real-time Progress**: Visual feedback during file processing
- **Results Display**: View similar cases with similarity scores
- **Case Details**: See metadata and details for each case
- **Case Download**: Download similar case files
- **Error Handling**: User-friendly error messages
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Configurable Backend**: Easy configuration for different environments

## Configuration

The frontend uses a two-tier configuration system:

### Development (Automatic)

When running on `localhost` or `127.0.0.1`, the frontend automatically uses:
```
Backend URL: http://localhost:8000
```

No configuration needed!

### Production (Environment Variable)

For production deployment, set the `BACKEND_URL` environment variable:

```bash
# Linux/Mac
export BACKEND_URL=https://your-api.onrender.com
bash build.sh

# Windows PowerShell
$env:BACKEND_URL="https://your-api.onrender.com"
.\build.ps1
```

The build script generates `js/env.js` from `js/env.js.template` with your backend URL.

## Build Process

### What the Build Script Does

1. Reads `BACKEND_URL` environment variable
2. Generates `js/env.js` from `js/env.js.template`
3. Replaces `${BACKEND_URL}` placeholder with actual URL
4. Validates the generated file

### Build Scripts

**Linux/Mac (bash)**:
```bash
bash build.sh
```

**Windows (PowerShell)**:
```powershell
.\build.ps1
# OR
.\build.ps1 -BackendUrl "https://your-api.onrender.com"
```

### Generated Files

- `js/env.js` - Generated during build (gitignored)
  - Contains production backend URL
  - Loaded before other scripts
  - Should never be committed to repository

## Deployment Platforms

The frontend can be deployed to any static hosting service:

### Recommended Platforms

- **Netlify** ⭐ - Easy setup, automatic deployments, free SSL
- **Vercel** ⭐ - Great performance, automatic deployments, free SSL
- **GitHub Pages** - Free, requires manual build or GitHub Actions
- **Cloudflare Pages** - Fast CDN, automatic deployments
- **AWS S3 + CloudFront** - Scalable, enterprise-grade
- **Azure Static Web Apps** - Microsoft cloud platform
- **Google Cloud Storage** - Google cloud platform

### Platform Configuration

Pre-configured files are included:

- `netlify.toml` - Netlify configuration
- `vercel.json` - Vercel configuration

For other platforms, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Environment Variables

### Required

- `BACKEND_URL` - Backend API base URL (e.g., `https://your-api.onrender.com`)

### Optional

None. The frontend is fully configured with just the backend URL.

## API Integration

The frontend communicates with the backend via these endpoints:

- `POST /api/upload` - Upload PDF and get similar cases
- `GET /api/health` - Check backend health
- `GET /api/cases/{id}` - Get case details
- `GET /api/cases/{id}/download` - Download case file
- `GET /api/performance` - Get performance metrics

See backend API documentation at `https://your-backend-url/docs`

## CORS Configuration

The backend must be configured to allow requests from your frontend domain.

**Backend Configuration**:
```bash
# Set in backend environment variables
CORS_ORIGINS=https://your-frontend.netlify.app,https://your-frontend.vercel.app
```

**Development**:
```bash
# Backend automatically allows localhost
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Testing

### Manual Testing

1. **Local Testing**:
   ```bash
   cd frontend
   python -m http.server 8080
   ```
   Open `http://localhost:8080` and test functionality

2. **Production Build Testing**:
   ```bash
   export BACKEND_URL=https://your-api.onrender.com
   bash build.sh
   python -m http.server 8080
   ```
   Verify it connects to production backend

### Browser Testing

Test on multiple browsers:
- Chrome/Edge (Chromium)
- Firefox
- Safari
- Mobile browsers (iOS Safari, Chrome Mobile)

### Functionality Checklist

- [ ] Home page loads correctly
- [ ] Navigation works between pages
- [ ] File upload accepts PDF files
- [ ] File upload rejects non-PDF files
- [ ] Progress indicator shows during processing
- [ ] Results display with similarity scores
- [ ] Case details are visible
- [ ] Case download works
- [ ] Error messages display for failures
- [ ] Responsive design works on mobile
- [ ] CORS requests succeed
- [ ] No console errors

## Troubleshooting

### Common Issues

**CORS Errors**:
- Check backend `CORS_ORIGINS` includes your frontend domain
- Verify backend is using HTTPS (if frontend is HTTPS)
- Check browser console for specific error messages

**Wrong Backend URL**:
- Verify `BACKEND_URL` environment variable is set
- Check `js/env.js` was generated correctly
- Ensure `env.js` is loaded before `config.js` in HTML

**Build Fails**:
- Check `js/env.js.template` exists
- Verify build command is correct
- Check deployment logs for error messages

**404 on Refresh**:
- Configure redirects in hosting platform
- See platform-specific instructions in DEPLOYMENT.md

For more troubleshooting help, see [DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting).

## Development

### File Structure

- **HTML Files**: Static HTML pages
- **CSS Files**: Styles using vanilla CSS
- **JavaScript Files**: Vanilla JavaScript (no frameworks)

### Code Style

- Use ES6+ JavaScript features
- Follow consistent indentation (2 spaces)
- Add comments for complex logic
- Use meaningful variable names
- Keep functions small and focused

### Adding New Features

1. Update HTML structure if needed
2. Add styles to `css/styles.css`
3. Add JavaScript logic to appropriate file
4. Test locally before deploying
5. Update documentation

## Security

### Best Practices

- ✅ Always use HTTPS in production
- ✅ Never commit `js/env.js` (it's gitignored)
- ✅ Use environment variables for configuration
- ✅ Configure specific CORS origins (not `*`)
- ✅ Enable security headers (see netlify.toml/vercel.json)
- ✅ Validate file types before upload
- ✅ Handle errors gracefully

### Security Headers

Pre-configured in `netlify.toml` and `vercel.json`:
- `X-Frame-Options: DENY` - Prevent clickjacking
- `X-Content-Type-Options: nosniff` - Prevent MIME sniffing
- `Referrer-Policy: no-referrer` - Control referrer information
- `X-XSS-Protection: 1; mode=block` - XSS protection

## Performance

### Optimization

- Static files are cached with appropriate headers
- CSS and JavaScript are minified (optional)
- Images are optimized (when added)
- CDN delivery via hosting platform

### Monitoring

Use platform analytics:
- Netlify Analytics
- Vercel Analytics
- Google Analytics (optional)

## Documentation

- **README.md** (this file) - Overview and quick start
- **QUICK_START.md** - Quick deployment guide
- **DEPLOYMENT.md** - Comprehensive deployment instructions
- **js/README.md** - JavaScript files documentation

## Support

### Getting Help

1. Check [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section
2. Check browser console for errors
3. Check network tab for failed requests
4. Check backend logs for API errors
5. Verify backend is accessible at its URL

### Backend Documentation

- Backend API: Visit your backend URL (e.g., `https://your-api.onrender.com`)
- Interactive docs: Visit `https://your-api.onrender.com/docs`
- Backend README: See `../README.md`

## Contributing

When contributing to the frontend:

1. Test locally before committing
2. Test on multiple browsers
3. Test responsive design on mobile
4. Update documentation if needed
5. Don't commit `js/env.js` (it's gitignored)

## License

[Add your license information here]

## Additional Resources

- [Netlify Documentation](https://docs.netlify.com/)
- [Vercel Documentation](https://vercel.com/docs)
- [MDN Web Docs](https://developer.mozilla.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Ready to deploy?** See [QUICK_START.md](QUICK_START.md) for a quick guide or [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.
