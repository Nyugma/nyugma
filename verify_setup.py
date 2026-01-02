#!/usr/bin/env python3
"""
Setup verification script for Legal Case Similarity Web Application
"""

import sys
import logging
from pathlib import Path

def verify_dependencies():
    """Verify all required dependencies can be imported"""
    print("Verifying dependencies...")
    
    try:
        import fastapi
        print(f"✓ FastAPI {fastapi.__version__}")
    except ImportError as e:
        print(f"✗ FastAPI: {e}")
        return False
    
    try:
        import uvicorn
        print(f"✓ Uvicorn {uvicorn.__version__}")
    except ImportError as e:
        print(f"✗ Uvicorn: {e}")
        return False
    
    try:
        import fitz
        print(f"✓ PyMuPDF {fitz.version[0]}")
    except ImportError as e:
        print(f"✗ PyMuPDF: {e}")
        return False
    
    try:
        import sklearn
        print(f"✓ scikit-learn {sklearn.__version__}")
    except ImportError as e:
        print(f"✗ scikit-learn: {e}")
        return False
    
    try:
        import nltk
        print(f"✓ NLTK {nltk.__version__}")
    except ImportError as e:
        print(f"✗ NLTK: {e}")
        return False
    
    try:
        import numpy
        print(f"✓ NumPy {numpy.__version__}")
    except ImportError as e:
        print(f"✗ NumPy: {e}")
        return False
    
    try:
        import pydantic
        print(f"✓ Pydantic {pydantic.__version__}")
    except ImportError as e:
        print(f"✗ Pydantic: {e}")
        return False
    
    try:
        import hypothesis
        print(f"✓ Hypothesis {hypothesis.__version__}")
    except ImportError as e:
        print(f"✗ Hypothesis: {e}")
        return False
    
    return True

def verify_project_structure():
    """Verify project directory structure"""
    print("\nVerifying project structure...")
    
    base_dir = Path(__file__).parent
    required_dirs = [
        "src",
        "src/components",
        "src/models", 
        "src/api",
        "src/config",
        "data",
        "data/cases",
        "data/vectors",
        "tests",
        "tests/unit",
        "tests/property",
        "static",
        "static/css",
        "static/js",
        "templates",
        "logs"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if full_path.exists():
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ {dir_path}/ (missing)")
            all_exist = False
    
    return all_exist

def verify_configuration():
    """Verify configuration files and settings"""
    print("\nVerifying configuration...")
    
    try:
        from src.config.settings import settings
        print(f"✓ Settings loaded: {settings.APP_NAME}")
        print(f"  - Vocabulary size: {settings.VOCABULARY_SIZE}")
        print(f"  - Max file size: {settings.MAX_FILE_SIZE // (1024*1024)}MB")
        print(f"  - Default search results: {settings.DEFAULT_SEARCH_RESULTS}")
    except Exception as e:
        print(f"✗ Settings: {e}")
        return False
    
    try:
        from src.config.logging_config import setup_logging
        setup_logging()
        logger = logging.getLogger("verify_setup")
        logger.info("Logging test message")
        print("✓ Logging configuration working")
    except Exception as e:
        print(f"✗ Logging: {e}")
        return False
    
    return True

def verify_api():
    """Verify FastAPI application"""
    print("\nVerifying API...")
    
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test root endpoint
        response = client.get("/")
        if response.status_code == 200:
            print("✓ Root endpoint working")
        else:
            print(f"✗ Root endpoint failed: {response.status_code}")
            return False
        
        # Test health endpoint
        response = client.get("/api/health")
        if response.status_code == 200:
            print("✓ Health endpoint working")
        else:
            print(f"✗ Health endpoint failed: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"✗ API: {e}")
        return False
    
    return True

def main():
    """Main verification function"""
    print("Legal Case Similarity Web Application - Setup Verification")
    print("=" * 60)
    
    success = True
    
    success &= verify_dependencies()
    success &= verify_project_structure()
    success &= verify_configuration()
    success &= verify_api()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ All verification checks passed!")
        print("The project is ready for development.")
        return 0
    else:
        print("✗ Some verification checks failed.")
        print("Please fix the issues above before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())