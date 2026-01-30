"""
Similarity search engine for legal case similarity analysis.
"""

import numpy as np
from typing import List, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity
from ..models.search_result import SearchResult


class SimilaritySearchEngine:
    """
    Implements similarity search using cosine similarity and K-Nearest Neighbors.
    
    This class provides functionality to search for similar legal cases by comparing
    TF-IDF vectors using cosine similarity and returning the top-k most similar results.
    """
    
    def __init__(self, case_vectors: np.ndarray, case_metadata: List[Dict[str, Any]]):
        """
        Initialize the similarity search engine.
        
        Args:
            case_vectors: Pre-computed TF-IDF vectors for all cases (n_cases x n_features)
            case_metadata: List of metadata dictionaries for each case
        """
        if case_vectors.shape[0] != len(case_metadata):
            raise ValueError(
                f"Number of vectors ({case_vectors.shape[0]}) must match "
                f"number of metadata entries ({len(case_metadata)})"
            )
        
        self.case_vectors = case_vectors
        self.case_metadata = case_metadata
    
    def search(self, query_vector: np.ndarray, k: int = 10) -> List[SearchResult]:
        """
        Search for the top-k most similar cases to the query.
        
        Args:
            query_vector: TF-IDF vector for the query document (1 x n_features)
            k: Number of top results to return (default: 10)
            
        Returns:
            List of SearchResult objects ordered by similarity score (descending)
        """
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        
        if query_vector.shape[1] != self.case_vectors.shape[1]:
            raise ValueError(
                f"Query vector dimension ({query_vector.shape[1]}) must match "
                f"case vectors dimension ({self.case_vectors.shape[1]})"
            )
        
        # Calculate cosine similarity between query and all cases
        similarities = cosine_similarity(query_vector, self.case_vectors)[0]
        
        # Get top-k indices sorted by similarity (descending)
        top_k_indices = np.argsort(similarities)[::-1][:k]
        
        # Create SearchResult objects
        results = []
        for idx in top_k_indices:
            metadata = self.case_metadata[idx]
            similarity_score = float(similarities[idx])
            
            # Create snippet from metadata if available, otherwise use title
            snippet = metadata.get('snippet', metadata.get('title', ''))[:200]
            
            result = SearchResult(
                case_id=metadata['case_id'],
                title=metadata['title'],
                date=metadata['date'],
                similarity_score=similarity_score,
                snippet=snippet,
                file_path=metadata['file_path']
            )
            results.append(result)
        
        return results
    
    def calculate_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        if vec1.ndim == 1:
            vec1 = vec1.reshape(1, -1)
        if vec2.ndim == 1:
            vec2 = vec2.reshape(1, -1)
            
        similarity = cosine_similarity(vec1, vec2)[0, 0]
        return float(similarity)
    
    def get_case_count(self) -> int:
        """
        Get the total number of cases in the repository.
        
        Returns:
            Number of cases
        """
        return len(self.case_metadata)
    
    def get_vector_dimensions(self) -> int:
        """
        Get the dimensionality of the case vectors.
        
        Returns:
            Number of features in each vector
        """
        return self.case_vectors.shape[1]