"""
Components package for Legal Case Similarity Application

This package contains the core processing components:
- PDFProcessor: PDF text extraction and validation
- TextPreprocessor: Text normalization and preprocessing
- LegalVectorizer: TF-IDF vectorization using legal vocabulary
- SimilaritySearchEngine: Cosine similarity search and K-NN retrieval
- CaseRepository: Case document and vector storage management
"""

from .pdf_processor import PDFProcessor
from .text_preprocessor import TextPreprocessor
from .legal_vectorizer import LegalVectorizer
from .similarity_search_engine import SimilaritySearchEngine
from .case_repository import CaseRepository

__all__ = ['PDFProcessor', 'TextPreprocessor', 'LegalVectorizer', 'SimilaritySearchEngine', 'CaseRepository']