###############################################################################
# Frontend Build Script (PowerShell)
# 
# This script generates the env.js file from environment variables for
# production deployment. It reads the BACKEND_URL environment variable
# and creates a JavaScript file that the frontend can use to configure
# the API endpoint.
#
# Usage:
#   $env:BACKEND_URL="https://your-api.onrender.com"; .\build.ps1
#   # OR
#   .\build.ps1 -BackendUrl "https://your-api.onrender.com"
#
# The script will:
#   1. Check if BACKEND_URL is set
#   2. Generate js/env.js from js/env.js.template
#   3. Validate the generated file
#
# For local development, this script is not needed - the frontend will
# automatically use localhost:8000 as the backend URL.
###############################################################################

param(
    [string]$BackendUrl = $env:BACKEND_URL
)

# Colors for output (using Write-Host -ForegroundColor instead of escape sequences)
function Write-ColorHost {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

Write-Host "=========================================="
Write-Host "Frontend Build Script (PowerShell)"
Write-Host "=========================================="
Write-Host ""

# Check if BACKEND_URL is set
if ([string]::IsNullOrEmpty($BackendUrl)) {
    Write-ColorHost "WARNING: BACKEND_URL environment variable is not set" "Yellow"
    Write-Host "Using placeholder value. Make sure to set BACKEND_URL in your deployment platform."
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  Netlify: Set in Site settings > Environment variables"
    Write-Host "  Vercel: Set in Project settings > Environment Variables"
    Write-Host "  GitHub Pages: Not supported (use default in config.js)"
    Write-Host ""
    $BackendUrl = "https://your-api.onrender.com"
}

Write-Host "Backend URL: $BackendUrl"
Write-Host ""

# Check if template exists
if (-not (Test-Path "js/env.js.template")) {
    Write-ColorHost "ERROR: js/env.js.template not found" "Red"
    Write-Host "Make sure you're running this script from the frontend directory."
    exit 1
}

# Generate env.js from template
Write-Host "Generating js/env.js from template..."
$template = Get-Content "js/env.js.template" -Raw
$output = $template -replace '\$\{BACKEND_URL\}', $BackendUrl
$output | Set-Content "js/env.js" -NoNewline

# Validate generated file
if (-not (Test-Path "js/env.js")) {
    Write-ColorHost "ERROR: Failed to generate js/env.js" "Red"
    exit 1
}

# Check if the file contains the actual URL (not the placeholder)
$generatedContent = Get-Content "js/env.js" -Raw
if ($generatedContent -match '\$\{BACKEND_URL\}') {
    Write-ColorHost "ERROR: Template variable was not replaced" "Red"
    exit 1
}

Write-ColorHost "✓ Successfully generated js/env.js" "Green"
Write-Host ""
Write-Host "Generated content:"
Write-Host "---"
Get-Content "js/env.js"
Write-Host "---"
Write-Host ""
Write-ColorHost "Build complete!" "Green"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Ensure env.js is loaded before config.js in your HTML files"
Write-Host "  2. Deploy your frontend to your hosting platform"
Write-Host "  3. Test that the frontend can connect to the backend"
