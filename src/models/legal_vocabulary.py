"""
Legal Vocabulary Model

This module provides the LegalVocabulary class for managing the curated legal terms
used in document vectorization.
"""

import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path


class LegalVocabulary:
    """
    Manages the legal vocabulary used for document vectorization.
    
    The vocabulary consists of 200-300 curated legal terms organized by categories
    such as civil procedure, contracts, property law, torts, etc.
    """
    
    def __init__(self, vocabulary_path: Optional[str] = None):
        """
        Initialize the LegalVocabulary.
        
        Args:
            vocabulary_path: Path to the legal_vocabulary.json file.
                           If None, uses default path in data directory.
        """
        if vocabulary_path is None:
            # Default path relative to project root
            project_root = Path(__file__).parent.parent.parent
            vocabulary_path = project_root / "data" / "legal_vocabulary.json"
        
        self.vocabulary_path = Path(vocabulary_path)
        self._terms: List[str] = []
        self._categories: Dict[str, List[str]] = {}
        self._weights: Dict[str, float] = {}
        
        self.load_vocabulary()
    
    def load_vocabulary(self) -> None:
        """
        Load the legal vocabulary from the JSON file.
        
        Raises:
            FileNotFoundError: If the vocabulary file doesn't exist.
            json.JSONDecodeError: If the vocabulary file is malformed.
        """
        if not self.vocabulary_path.exists():
            raise FileNotFoundError(f"Legal vocabulary file not found: {self.vocabulary_path}")
        
        try:
            with open(self.vocabulary_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._terms = data.get('terms', [])
            self._categories = data.get('categories', {})
            self._weights = data.get('weights', {})
            
            # Validate vocabulary size
            if not (200 <= len(self._terms) <= 300):
                raise ValueError(f"Legal vocabulary must contain 200-300 terms, found {len(self._terms)}")
                
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in vocabulary file: {e}")
    
    def save_vocabulary(self) -> None:
        """
        Save the current vocabulary to the JSON file.
        """
        data = {
            'terms': self._terms,
            'categories': self._categories,
            'weights': self._weights
        }
        
        # Ensure directory exists
        self.vocabulary_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.vocabulary_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @property
    def terms(self) -> List[str]:
        """Get the list of legal terms."""
        return self._terms.copy()
    
    @property
    def categories(self) -> Dict[str, List[str]]:
        """Get the categorized legal terms."""
        return self._categories.copy()
    
    @property
    def weights(self) -> Dict[str, float]:
        """Get the term weights (if any)."""
        return self._weights.copy()
    
    @property
    def size(self) -> int:
        """Get the number of terms in the vocabulary."""
        return len(self._terms)
    
    def get_terms_by_category(self, category: str) -> List[str]:
        """
        Get all terms belonging to a specific category.
        
        Args:
            category: The category name (e.g., 'civil_procedure', 'contracts')
        
        Returns:
            List of terms in the specified category.
        """
        return self._categories.get(category, []).copy()
    
    def get_category_for_term(self, term: str) -> Optional[str]:
        """
        Find which category a term belongs to.
        
        Args:
            term: The legal term to search for
        
        Returns:
            The category name if found, None otherwise.
        """
        for category, terms in self._categories.items():
            if term in terms:
                return category
        return None
    
    def add_term(self, term: str, category: Optional[str] = None, weight: Optional[float] = None) -> None:
        """
        Add a new term to the vocabulary.
        
        Args:
            term: The legal term to add
            category: Optional category for the term
            weight: Optional weight for the term
        """
        if term not in self._terms:
            self._terms.append(term)
        
        if category and category in self._categories:
            if term not in self._categories[category]:
                self._categories[category].append(term)
        
        if weight is not None:
            self._weights[term] = weight
    
    def remove_term(self, term: str) -> bool:
        """
        Remove a term from the vocabulary.
        
        Args:
            term: The term to remove
        
        Returns:
            True if the term was removed, False if it wasn't found.
        """
        if term in self._terms:
            self._terms.remove(term)
            
            # Remove from categories
            for category_terms in self._categories.values():
                if term in category_terms:
                    category_terms.remove(term)
            
            # Remove weight if exists
            self._weights.pop(term, None)
            
            return True
        return False
    
    def validate_vocabulary(self) -> Dict[str, Any]:
        """
        Validate the vocabulary structure and content.
        
        Returns:
            Dictionary with validation results including any issues found.
        """
        issues = []
        
        # Check vocabulary size
        if not (200 <= len(self._terms) <= 300):
            issues.append(f"Vocabulary size {len(self._terms)} is outside required range 200-300")
        
        # Check for duplicate terms
        if len(self._terms) != len(set(self._terms)):
            duplicates = [term for term in set(self._terms) if self._terms.count(term) > 1]
            issues.append(f"Duplicate terms found: {duplicates}")
        
        # Check category consistency
        all_category_terms = set()
        for category, terms in self._categories.items():
            for term in terms:
                if term not in self._terms:
                    issues.append(f"Term '{term}' in category '{category}' not found in main vocabulary")
                all_category_terms.add(term)
        
        # Check for uncategorized terms
        uncategorized = set(self._terms) - all_category_terms
        if uncategorized:
            issues.append(f"Uncategorized terms: {list(uncategorized)}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'vocabulary_size': len(self._terms),
            'categories_count': len(self._categories),
            'categorized_terms': len(all_category_terms),
            'uncategorized_terms': len(uncategorized)
        }
    
    def __len__(self) -> int:
        """Return the number of terms in the vocabulary."""
        return len(self._terms)
    
    def __contains__(self, term: str) -> bool:
        """Check if a term is in the vocabulary."""
        return term in self._terms
    
    def __iter__(self):
        """Iterate over the terms in the vocabulary."""
        return iter(self._terms)
    
    def __repr__(self) -> str:
        """String representation of the vocabulary."""
        return f"LegalVocabulary(size={len(self._terms)}, categories={len(self._categories)})"