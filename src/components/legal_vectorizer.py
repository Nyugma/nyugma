"""
Legal Vectorizer Component

This module provides the LegalVectorizer class for converting legal documents
into TF-IDF vectors using a curated legal vocabulary.
"""

import pickle
import numpy as np
from pathlib import Path
from typing import List, Union, Optional, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.exceptions import NotFittedError

from ..models.legal_vocabulary import LegalVocabulary


class LegalVectorizer:
    """
    Converts legal documents into TF-IDF vectors using a curated legal vocabulary.
    
    This class uses scikit-learn's TfidfVectorizer with a fixed legal vocabulary
    to ensure consistent vectorization across all documents. The vectorizer can
    be trained on a corpus of documents and then used to transform new documents
    into the same vector space.
    """
    
    def __init__(self, vocabulary: Optional[LegalVocabulary] = None, **kwargs):
        """
        Initialize the LegalVectorizer.
        
        Args:
            vocabulary: LegalVocabulary instance. If None, loads default vocabulary.
            **kwargs: Additional parameters for TfidfVectorizer
        """
        if vocabulary is None:
            vocabulary = LegalVocabulary()
        
        self.vocabulary = vocabulary
        
        # Default TF-IDF parameters optimized for legal documents
        default_params = {
            'vocabulary': {term: idx for idx, term in enumerate(vocabulary.terms)},
            'sublinear_tf': True,
            'stop_words': 'english',
            'max_df': 0.8,
            'min_df': 2,
            'lowercase': True,
            'token_pattern': r'\b[a-zA-Z][a-zA-Z]+\b'  # Only alphabetic tokens, min 2 chars
        }
        
        # Override defaults with any provided kwargs
        default_params.update(kwargs)
        
        self.vectorizer = TfidfVectorizer(**default_params)
        self._is_fitted = False
        self._feature_names = None
    
    def fit(self, documents: List[str]) -> 'LegalVectorizer':
        """
        Fit the vectorizer on a corpus of documents.
        
        Args:
            documents: List of document texts to fit the vectorizer on
            
        Returns:
            Self for method chaining
            
        Raises:
            ValueError: If documents list is empty
        """
        if not documents:
            raise ValueError("Documents list cannot be empty")
        
        # Fit the vectorizer
        self.vectorizer.fit(documents)
        self._is_fitted = True
        self._feature_names = self.vectorizer.get_feature_names_out()
        
        return self
    
    def transform(self, documents: Union[str, List[str]]) -> np.ndarray:
        """
        Transform documents into TF-IDF vectors.
        
        Args:
            documents: Single document string or list of document strings
            
        Returns:
            TF-IDF matrix as numpy array. Shape: (n_documents, n_features)
            
        Raises:
            NotFittedError: If vectorizer hasn't been fitted yet
        """
        if not self._is_fitted:
            raise NotFittedError("Vectorizer must be fitted before transforming documents")
        
        # Handle single document
        if isinstance(documents, str):
            documents = [documents]
        
        # Transform documents
        tfidf_matrix = self.vectorizer.transform(documents)
        
        # Convert sparse matrix to dense numpy array
        return tfidf_matrix.toarray()
    
    def fit_transform(self, documents: List[str]) -> np.ndarray:
        """
        Fit the vectorizer and transform documents in one step.
        
        Args:
            documents: List of document texts
            
        Returns:
            TF-IDF matrix as numpy array
        """
        return self.fit(documents).transform(documents)
    
    def get_feature_names(self) -> List[str]:
        """
        Get the feature names (vocabulary terms) used by the vectorizer.
        
        Returns:
            List of feature names
            
        Raises:
            NotFittedError: If vectorizer hasn't been fitted yet
        """
        if not self._is_fitted:
            raise NotFittedError("Vectorizer must be fitted before accessing feature names")
        
        return list(self._feature_names)
    
    def get_vector_dimension(self) -> int:
        """
        Get the dimensionality of the vectors produced by this vectorizer.
        
        Returns:
            Number of dimensions in the output vectors
            
        Raises:
            NotFittedError: If vectorizer hasn't been fitted yet
        """
        if not self._is_fitted:
            raise NotFittedError("Vectorizer must be fitted before accessing dimensions")
        
        return len(self._feature_names)
    
    def save_model(self, path: Union[str, Path]) -> None:
        """
        Save the fitted vectorizer model to disk using pickle.
        
        Args:
            path: File path to save the model
            
        Raises:
            NotFittedError: If vectorizer hasn't been fitted yet
        """
        if not self._is_fitted:
            raise NotFittedError("Cannot save unfitted vectorizer")
        
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save both the vectorizer and metadata
        model_data = {
            'vectorizer': self.vectorizer,
            'vocabulary_size': len(self.vocabulary.terms),
            'feature_names': self._feature_names,
            'is_fitted': self._is_fitted
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, path: Union[str, Path]) -> 'LegalVectorizer':
        """
        Load a fitted vectorizer model from disk.
        
        Args:
            path: File path to load the model from
            
        Returns:
            Self for method chaining
            
        Raises:
            FileNotFoundError: If model file doesn't exist
            pickle.PickleError: If model file is corrupted
        """
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        
        try:
            with open(path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.vectorizer = model_data['vectorizer']
            self._feature_names = model_data['feature_names']
            self._is_fitted = model_data['is_fitted']
            
            return self
            
        except (pickle.PickleError, KeyError) as e:
            raise pickle.PickleError(f"Failed to load model: {e}")
    
    def get_top_features(self, document: str, n_features: int = 10) -> List[tuple]:
        """
        Get the top N features (terms) with highest TF-IDF scores for a document.
        
        Args:
            document: Document text to analyze
            n_features: Number of top features to return
            
        Returns:
            List of (feature_name, score) tuples sorted by score descending
            
        Raises:
            NotFittedError: If vectorizer hasn't been fitted yet
        """
        if not self._is_fitted:
            raise NotFittedError("Vectorizer must be fitted before analyzing features")
        
        # Transform the document
        vector = self.transform([document])[0]
        
        # Get feature names and scores
        feature_names = self.get_feature_names()
        
        # Create list of (feature, score) tuples
        feature_scores = [(feature_names[i], vector[i]) for i in range(len(vector)) if vector[i] > 0]
        
        # Sort by score descending and return top N
        feature_scores.sort(key=lambda x: x[1], reverse=True)
        
        return feature_scores[:n_features]
    
    def calculate_similarity(self, doc1: str, doc2: str) -> float:
        """
        Calculate cosine similarity between two documents.
        
        Args:
            doc1: First document text
            doc2: Second document text
            
        Returns:
            Cosine similarity score between 0 and 1
            
        Raises:
            NotFittedError: If vectorizer hasn't been fitted yet
        """
        if not self._is_fitted:
            raise NotFittedError("Vectorizer must be fitted before calculating similarity")
        
        # Transform both documents
        vectors = self.transform([doc1, doc2])
        vec1, vec2 = vectors[0], vectors[1]
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        # Handle zero vectors
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Ensure result is between 0 and 1 (handle floating point errors)
        return max(0.0, min(1.0, similarity))
    
    @property
    def is_fitted(self) -> bool:
        """Check if the vectorizer has been fitted."""
        return self._is_fitted
    
    @property
    def vocabulary_size(self) -> int:
        """Get the size of the vocabulary."""
        return len(self.vocabulary.terms)
    
    def get_vectorizer_params(self) -> Dict[str, Any]:
        """
        Get the parameters used by the underlying TfidfVectorizer.
        
        Returns:
            Dictionary of vectorizer parameters
        """
        return self.vectorizer.get_params()
    
    def __repr__(self) -> str:
        """String representation of the vectorizer."""
        status = "fitted" if self._is_fitted else "not fitted"
        return f"LegalVectorizer(vocabulary_size={self.vocabulary_size}, status={status})"