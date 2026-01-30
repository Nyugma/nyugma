"""
Basic setup tests to verify project structure and dependencies
"""

import pytest
import sys
from pathlib import Path

def test_project_structure():
    """Test that all required directories exist"""
    base_dir = Path(__file__).parent.parent
    
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
    
    for dir_path in required_dirs:
        assert (base_dir / dir_path).exists(), f"Directory {dir_path} does not exist"

def test_core_dependencies():
    """Test that core dependencies can be imported"""
    try:
        import fastapi
        import uvicorn
        import fitz  # PyMuPDF
        import sklearn
        import nltk
        import numpy
        import pydantic
        import hypothesis
    except ImportError as e:
        pytest.fail(f"Failed to import required dependency: {e}")

def test_settings_import():
    """Test that settings can be imported"""
    from src.config.settings import settings
    assert settings.APP_NAME == "Legal Case Similarity"
    assert settings.VOCABULARY_SIZE == 300

def test_logging_config():
    """Test that logging configuration works"""
    from src.config.logging_config import setup_logging
    import logging
    
    setup_logging()
    logger = logging.getLogger("test")
    logger.info("Test logging message")
    
    # Verify logger is configured
    assert logger.level <= logging.INFO