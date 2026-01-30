#!/bin/bash

###############################################################################
# Frontend Build Script
# 
# This script generates the env.js file from environment variables for
# production deployment. It reads the BACKEND_URL environment variable
# and creates a JavaScript file that the frontend can use to configure
# the API endpoint.
#
# Usage:
#   BACKEND_URL=https://your-api.onrender.com ./build.sh
#
# The script will:
#   1. Check if BACKEND_URL is set
#   2. Generate js/env.js from js/env.js.template
#   3. Validate the generated file
#
# For local development, this script is not needed - the frontend will
# automatically use localhost:8000 as the backend URL.
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Frontend Build Script"
echo "=========================================="
echo ""

# Check if BACKEND_URL is set
if [ -z "$BACKEND_URL" ]; then
    echo -e "${YELLOW}WARNING: BACKEND_URL environment variable is not set${NC}"
    echo "Using placeholder value. Make sure to set BACKEND_URL in your deployment platform."
    echo ""
    echo "Examples:"
    echo "  Netlify: Set in Site settings > Environment variables"
    echo "  Vercel: Set in Project settings > Environment Variables"
    echo "  GitHub Pages: Not supported (use default in config.js)"
    echo ""
    BACKEND_URL="https://your-api.onrender.com"
fi

echo "Backend URL: $BACKEND_URL"
echo ""

# Check if template exists
if [ ! -f "js/env.js.template" ]; then
    echo -e "${RED}ERROR: js/env.js.template not found${NC}"
    echo "Make sure you're running this script from the frontend directory."
    exit 1
fi

# Generate env.js from template
echo "Generating js/env.js from template..."
cat js/env.js.template | sed "s|\${BACKEND_URL}|$BACKEND_URL|g" > js/env.js

# Validate generated file
if [ ! -f "js/env.js" ]; then
    echo -e "${RED}ERROR: Failed to generate js/env.js${NC}"
    exit 1
fi

# Check if the file contains the actual URL (not the placeholder)
if grep -q "\${BACKEND_URL}" js/env.js; then
    echo -e "${RED}ERROR: Template variable was not replaced${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Successfully generated js/env.js${NC}"
echo ""
echo "Generated content:"
echo "---"
cat js/env.js
echo "---"
echo ""
echo -e "${GREEN}Build complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Ensure env.js is loaded before config.js in your HTML files"
echo "  2. Deploy your frontend to your hosting platform"
echo "  3. Test that the frontend can connect to the backend"
