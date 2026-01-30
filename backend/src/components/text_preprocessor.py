"""
Text Preprocessing Component for Legal Case Similarity Application

This module provides functionality to normalize and clean extracted text
for vectorization using NLTK for stopword filtering and lemmatization.
"""

import re
import string
from typing import List, Optional
import logging
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

logger = logging.getLogger(__name__)


class TextPreprocessor:
    """
    Handles text normalization and preprocessing for legal documents.
    
    This class provides methods to:
    - Normalize text by converting to lowercase and removing punctuation
    - Filter out standard English stopwords using NLTK
    - Apply optional lemmatization for word normalization
    - Ensure consistent preprocessing across all documents
    """
    
    def __init__(self, enable_lemmatization: bool = True):
        """
        Initialize the text preprocessor.
        
        Args:
            enable_lemmatization (bool): Whether to enable lemmatization processing
        """
        self.enable_lemmatization = enable_lemmatization
        self.lemmatizer = None
        self.stopwords_set = None
        
        # Download required NLTK data
        self._download_nltk_data()
        
        # Initialize components
        self._initialize_components()
    
    def _download_nltk_data(self) -> None:
        """
        Download required NLTK data packages.
        
        Downloads stopwords, punkt tokenizer, wordnet, and averaged_perceptron_tagger
        if they are not already available.
        """
        try:
            # Required NLTK data packages
            nltk_packages = [
                'stopwords',
                'punkt', 
                'wordnet',
                'averaged_perceptron_tagger',
                'omw-1.4'  # Open Multilingual Wordnet for lemmatization
            ]
            
            for package in nltk_packages:
                try:
                    nltk.data.find(f'tokenizers/{package}')
                except LookupError:
                    try:
                        nltk.data.find(f'corpora/{package}')
                    except LookupError:
                        try:
                            nltk.data.find(f'taggers/{package}')
                        except LookupError:
                            logger.info(f"Downloading NLTK package: {package}")
                            nltk.download(package, quiet=True)
                            
        except Exception as e:
            logger.warning(f"Failed to download some NLTK data: {e}")
    
    def _initialize_components(self) -> None:
        """
        Initialize NLTK components for text processing.
        """
        try:
            # Initialize stopwords
            self.stopwords_set = set(stopwords.words('english'))
            logger.info(f"Loaded {len(self.stopwords_set)} English stopwords")
            
            # Initialize lemmatizer if enabled
            if self.enable_lemmatization:
                self.lemmatizer = WordNetLemmatizer()
                logger.info("Lemmatizer initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize text preprocessing components: {e}")
            # Fallback to basic stopwords if NLTK fails
            self.stopwords_set = {
                'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
                'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
                'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
                'had', 'what', 'said', 'each', 'which', 'their', 'time', 'if'
            }
            self.lemmatizer = None
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text by converting to lowercase and removing punctuation.
        
        Applies consistent text normalization including:
        - Convert to lowercase
        - Remove punctuation marks
        - Remove extra whitespace
        - Preserve word boundaries
        
        Args:
            text (str): Raw text to normalize
            
        Returns:
            str: Normalized text string
            
        Requirements: 1.4, 8.1, 8.2 - Text normalization
        """
        if not text or not isinstance(text, str):
            return ""
        
        try:
            # Convert to lowercase
            normalized = text.lower()
            
            # Remove punctuation but preserve word boundaries
            # Replace punctuation with spaces to avoid word concatenation
            normalized = re.sub(r'[^\w\s]', ' ', normalized)
            
            # Remove extra whitespace and normalize spaces
            normalized = re.sub(r'\s+', ' ', normalized).strip()
            
            return normalized
            
        except Exception as e:
            logger.error(f"Text normalization failed: {e}")
            return ""
    
    def tokenize_text(self, text: str) -> List[str]:
        """
        Tokenize normalized text into individual words.
        
        Args:
            text (str): Normalized text to tokenize
            
        Returns:
            List[str]: List of individual word tokens
        """
        if not text:
            return []
        
        try:
            # Use NLTK word tokenizer if available
            tokens = word_tokenize(text)
            return [token for token in tokens if token.isalpha()]
            
        except Exception as e:
            logger.warning(f"NLTK tokenization failed, using basic split: {e}")
            # Fallback to simple whitespace tokenization
            return [word for word in text.split() if word.isalpha()]
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Remove standard English stopwords from token list.
        
        Filters out common English words that don't contribute to document meaning
        using NLTK's stopwords corpus.
        
        Args:
            tokens (List[str]): List of word tokens
            
        Returns:
            List[str]: Filtered tokens with stopwords removed
            
        Requirements: 1.5 - Stopword filtering
        """
        if not tokens:
            return []
        
        try:
            # Filter out stopwords and very short words
            filtered_tokens = [
                token for token in tokens 
                if token.lower() not in self.stopwords_set 
                and len(token) > 2  # Remove very short words
            ]
            
            return filtered_tokens
            
        except Exception as e:
            logger.error(f"Stopword removal failed: {e}")
            return tokens
    
    def lemmatize_tokens(self, tokens: List[str]) -> List[str]:
        """
        Apply lemmatization to reduce words to their base forms.
        
        Converts related word forms to their dictionary base form
        (e.g., "children" -> "child", "running" -> "run").
        
        Args:
            tokens (List[str]): List of word tokens to lemmatize
            
        Returns:
            List[str]: List of lemmatized tokens
            
        Requirements: 8.3 - Lemmatization consistency
        """
        if not tokens or not self.enable_lemmatization or not self.lemmatizer:
            return tokens
        
        try:
            lemmatized_tokens = []
            
            for token in tokens:
                try:
                    # Apply lemmatization (default to noun if POS tagging fails)
                    lemmatized = self.lemmatizer.lemmatize(token.lower())
                    lemmatized_tokens.append(lemmatized)
                    
                except Exception as e:
                    logger.warning(f"Lemmatization failed for token '{token}': {e}")
                    # Keep original token if lemmatization fails
                    lemmatized_tokens.append(token.lower())
            
            return lemmatized_tokens
            
        except Exception as e:
            logger.error(f"Lemmatization process failed: {e}")
            return [token.lower() for token in tokens]
    
    def preprocess(self, text: str) -> str:
        """
        Apply complete preprocessing pipeline to input text.
        
        Performs the full text preprocessing workflow:
        1. Text normalization (lowercase, punctuation removal)
        2. Tokenization
        3. Stopword removal
        4. Optional lemmatization
        5. Rejoin tokens into processed text string
        
        Args:
            text (str): Raw text to preprocess
            
        Returns:
            str: Fully preprocessed text ready for vectorization
            
        Requirements: 1.4, 1.5, 8.1, 8.2, 8.3, 8.4, 8.5 - Complete preprocessing
        """
        if not text or not isinstance(text, str):
            return ""
        
        try:
            # Step 1: Normalize text
            normalized_text = self.normalize_text(text)
            if not normalized_text:
                return ""
            
            # Step 2: Tokenize
            tokens = self.tokenize_text(normalized_text)
            if not tokens:
                return ""
            
            # Step 3: Remove stopwords
            filtered_tokens = self.remove_stopwords(tokens)
            
            # Step 4: Apply lemmatization if enabled
            if self.enable_lemmatization:
                processed_tokens = self.lemmatize_tokens(filtered_tokens)
            else:
                processed_tokens = [token.lower() for token in filtered_tokens]
            
            # Step 5: Rejoin tokens
            processed_text = ' '.join(processed_tokens)
            
            logger.debug(f"Preprocessed text: {len(text)} -> {len(processed_text)} characters")
            return processed_text
            
        except Exception as e:
            logger.error(f"Text preprocessing failed: {e}")
            return ""
    
    def preprocess_batch(self, texts: List[str]) -> List[str]:
        """
        Apply preprocessing to a batch of texts efficiently.
        
        Args:
            texts (List[str]): List of raw texts to preprocess
            
        Returns:
            List[str]: List of preprocessed texts
            
        Requirements: 8.4, 8.5 - Consistent preprocessing
        """
        if not texts:
            return []
        
        try:
            processed_texts = []
            
            for i, text in enumerate(texts):
                try:
                    processed = self.preprocess(text)
                    processed_texts.append(processed)
                    
                except Exception as e:
                    logger.warning(f"Failed to preprocess text {i}: {e}")
                    processed_texts.append("")
            
            return processed_texts
            
        except Exception as e:
            logger.error(f"Batch preprocessing failed: {e}")
            return [""] * len(texts)