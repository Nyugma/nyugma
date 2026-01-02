#!/bin/bash
# Installation script for Legal Case Similarity Web Application
# Supports: Linux (Ubuntu/Debian, CentOS/RHEL/Fedora) and macOS

set -e  # Exit on error

echo "=========================================="
echo "Legal Case Similarity - Installation"
echo "=========================================="
echo ""

# Detect operating system
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [ -f /etc/debian_version ]; then
        OS="debian"
    elif [ -f /etc/redhat-release ]; then
        OS="redhat"
    else
        OS="linux"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "Unsupported operating system: $OSTYPE"
    exit 1
fi

echo "Detected OS: $OS"
echo ""

# Check Python version
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "Python version: $PYTHON_VERSION"
    
    # Check if version is 3.8 or higher
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        echo "Error: Python 3.8 or higher is required"
        exit 1
    fi
else
    echo "Python 3 not found. Installing..."
    
    case $OS in
        debian)
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv
            ;;
        redhat)
            sudo dnf install -y python3 python3-pip python3-virtualenv || \
            sudo yum install -y python3 python3-pip
            ;;
        macos)
            if ! command -v brew &> /dev/null; then
                echo "Homebrew not found. Please install Homebrew first:"
                echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
                exit 1
            fi
            brew install python@3.11
            ;;
    esac
fi

echo ""
echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Upgrading pip..."
pip install --upgrade pip

echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Downloading NLTK data..."
python3 << EOF
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
print("NLTK data downloaded successfully")
EOF

echo ""
echo "Creating necessary directories..."
mkdir -p data/cases
mkdir -p data/vectors
mkdir -p logs
mkdir -p static/css
mkdir -p static/js
mkdir -p templates

echo ""
echo "Verifying installation..."
if python3 verify_setup.py; then
    echo ""
    echo "=========================================="
    echo "Installation completed successfully!"
    echo "=========================================="
    echo ""
    echo "To start the application:"
    echo "  1. Activate virtual environment: source venv/bin/activate"
    echo "  2. Run development server: python run_api.py"
    echo "  3. Run production server: python uvicorn_production.py"
    echo ""
    echo "The application will be available at: http://localhost:8000"
    echo ""
    echo "For more information, see:"
    echo "  - README.md for general documentation"
    echo "  - DEPLOYMENT.md for deployment instructions"
    echo "  - PRODUCTION_CHECKLIST.md for production deployment"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "Installation completed with warnings"
    echo "=========================================="
    echo ""
    echo "Please review the verification output above."
    echo "Some components may need manual configuration."
    echo ""
fi
