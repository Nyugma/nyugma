"""
Application settings and configuration
"""

import os
from pathlib import Path
from typing import List

class Settings:
    """Application settings"""
    
    # Application settings
    APP_NAME: str = "Legal Case Similarity"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # API settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # File upload settings
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf"]
    
    # Data directories
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    CASES_DIR: Path = DATA_DIR / "cases"
    VECTORS_DIR: Path = DATA_DIR / "vectors"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # Legal vocabulary settings
    VOCABULARY_SIZE: int = 300
    MIN_VOCABULARY_SIZE: int = 200
    MAX_VOCABULARY_SIZE: int = 300
    
    # TF-IDF settings
    MAX_DF: float = 0.8
    MIN_DF: int = 2
    SUBLINEAR_TF: bool = True
    
    # Search settings
    DEFAULT_SEARCH_RESULTS: int = 10
    MAX_SEARCH_RESULTS: int = 50
    
    # Performance settings
    MAX_SEARCH_TIME_SECONDS: int = 10
    MAX_CONCURRENT_UPLOADS: int = 5
    
    # Repository settings
    MIN_REPOSITORY_SIZE: int = 500
    MAX_REPOSITORY_SIZE: int = 1000

# Global settings instance
settings = Settings()