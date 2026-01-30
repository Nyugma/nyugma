"""
Case repository management for legal case similarity system.
"""

import json
import pickle
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np
from ..models.case_document import CaseDocument


class CaseRepository:
    """
    Manages the repository of legal cases including metadata and vector storage.
    
    This class handles loading, storing, and retrieving case documents and their
    associated TF-IDF vectors for similarity search operations.
    """
    
    # Schema version for metadata validation
    SCHEMA_VERSION = "1.0"
    
    # Required fields for case metadata
    REQUIRED_CASE_FIELDS = {'case_id', 'title', 'date', 'file_path'}
    
    # Maximum repository capacity (as per requirements)
    MAX_REPOSITORY_SIZE = 1000
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the case repository.
        
        Args:
            data_dir: Base directory for data storage
        """
        self.data_dir = Path(data_dir)
        self.cases_dir = self.data_dir / "cases"
        self.vectors_dir = self.data_dir / "vectors"
        self.metadata_file = self.data_dir / "cases_metadata.json"
        
        # Ensure directories exist
        self.cases_dir.mkdir(parents=True, exist_ok=True)
        self.vectors_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize metadata file with proper schema if it doesn't exist
        if not self.metadata_file.exists():
            self._initialize_metadata_file()
    
    def _initialize_metadata_file(self) -> None:
        """
        Initialize the metadata file with proper schema.
        """
        initial_metadata = {
            "cases": [],
            "metadata": {
                "version": self.SCHEMA_VERSION,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_cases": 0,
                "schema_version": self.SCHEMA_VERSION
            }
        }
        self._save_metadata(initial_metadata)
    
    def _validate_case_metadata(self, case_data: Dict[str, Any]) -> List[str]:
        """
        Validate case metadata against required schema.
        
        Args:
            case_data: Case metadata dictionary to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check required fields
        missing_fields = self.REQUIRED_CASE_FIELDS - set(case_data.keys())
        if missing_fields:
            errors.append(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Validate field types and values
        if 'case_id' in case_data:
            if not isinstance(case_data['case_id'], str) or not case_data['case_id'].strip():
                errors.append("case_id must be a non-empty string")
        
        if 'title' in case_data:
            if not isinstance(case_data['title'], str) or not case_data['title'].strip():
                errors.append("title must be a non-empty string")
        
        if 'date' in case_data:
            if isinstance(case_data['date'], str):
                try:
                    datetime.fromisoformat(case_data['date'])
                except ValueError:
                    errors.append("date must be a valid ISO format datetime string")
            else:
                errors.append("date must be a string in ISO format")
        
        if 'file_path' in case_data:
            if not isinstance(case_data['file_path'], str) or not case_data['file_path'].strip():
                errors.append("file_path must be a non-empty string")
        
        # Validate vector_index if present
        if 'vector_index' in case_data:
            if not isinstance(case_data['vector_index'], int) or case_data['vector_index'] < 0:
                errors.append("vector_index must be a non-negative integer")
        
        # Validate metadata field if present
        if 'metadata' in case_data and case_data['metadata'] is not None:
            if not isinstance(case_data['metadata'], dict):
                errors.append("metadata must be a dictionary")
        
        return errors
    
    def _validate_metadata_structure(self, metadata: Dict[str, Any]) -> List[str]:
        """
        Validate the overall metadata file structure.
        
        Args:
            metadata: Complete metadata dictionary
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check top-level structure
        if 'cases' not in metadata:
            errors.append("Missing 'cases' field in metadata")
        elif not isinstance(metadata['cases'], list):
            errors.append("'cases' field must be a list")
        
        if 'metadata' not in metadata:
            errors.append("Missing 'metadata' field in metadata")
        elif not isinstance(metadata['metadata'], dict):
            errors.append("'metadata' field must be a dictionary")
        else:
            # Validate metadata section
            meta_section = metadata['metadata']
            required_meta_fields = {'version', 'created_at', 'last_updated', 'total_cases', 'schema_version'}
            missing_meta_fields = required_meta_fields - set(meta_section.keys())
            if missing_meta_fields:
                errors.append(f"Missing metadata fields: {', '.join(missing_meta_fields)}")
        
        return errors
    
    def load_case_metadata(self) -> List[Dict[str, Any]]:
        """
        Load case metadata from JSON file with validation.
        
        Returns:
            List of case metadata dictionaries
            
        Raises:
            ValueError: If metadata file is invalid or corrupted
        """
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate metadata structure
            structure_errors = self._validate_metadata_structure(data)
            if structure_errors:
                raise ValueError(f"Invalid metadata structure: {'; '.join(structure_errors)}")
            
            cases = data.get("cases", [])
            
            # Validate each case
            for i, case_data in enumerate(cases):
                case_errors = self._validate_case_metadata(case_data)
                if case_errors:
                    raise ValueError(f"Invalid case data at index {i}: {'; '.join(case_errors)}")
            
            return cases
            
        except FileNotFoundError:
            print(f"Warning: Metadata file not found: {self.metadata_file}")
            self._initialize_metadata_file()
            return []
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in metadata file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading metadata: {e}")
    
    def save_case_metadata(self, cases_metadata: List[Dict[str, Any]]) -> None:
        """
        Save case metadata to JSON file with validation.
        
        Args:
            cases_metadata: List of case metadata dictionaries
            
        Raises:
            ValueError: If case metadata is invalid
        """
        # Validate each case before saving
        for i, case_data in enumerate(cases_metadata):
            case_errors = self._validate_case_metadata(case_data)
            if case_errors:
                raise ValueError(f"Invalid case data at index {i}: {'; '.join(case_errors)}")
        
        # Check repository capacity
        if len(cases_metadata) > self.MAX_REPOSITORY_SIZE:
            raise ValueError(f"Repository capacity exceeded: {len(cases_metadata)} > {self.MAX_REPOSITORY_SIZE}")
        
        # Create complete metadata structure
        complete_metadata = {
            "cases": cases_metadata,
            "metadata": {
                "version": self.SCHEMA_VERSION,
                "created_at": self._get_creation_time(),
                "last_updated": datetime.now().isoformat(),
                "total_cases": len(cases_metadata),
                "schema_version": self.SCHEMA_VERSION
            }
        }
        
        self._save_metadata(complete_metadata)
    
    def _get_creation_time(self) -> str:
        """
        Get the creation time from existing metadata or use current time.
        
        Returns:
            ISO format datetime string
        """
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                return existing_data.get("metadata", {}).get("created_at", datetime.now().isoformat())
        except (FileNotFoundError, json.JSONDecodeError):
            return datetime.now().isoformat()
    
    def _save_metadata(self, data: Dict[str, Any]) -> None:
        """
        Save metadata dictionary to JSON file.
        
        Args:
            data: Metadata dictionary to save
        """
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_case_vectors(self) -> Optional[np.ndarray]:
        """
        Load pre-computed case vectors from pickle file.
        
        Returns:
            Array of case vectors or None if file doesn't exist
        """
        vectors_file = self.vectors_dir / "case_vectors.pkl"
        try:
            with open(vectors_file, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            print(f"Warning: Vector file not found: {vectors_file}")
            return None
        except Exception as e:
            print(f"Error loading vectors: {e}")
            return None
    
    def save_case_vectors(self, vectors: np.ndarray) -> None:
        """
        Save case vectors to pickle file.
        
        Args:
            vectors: Array of case vectors to save
        """
        vectors_file = self.vectors_dir / "case_vectors.pkl"
        with open(vectors_file, 'wb') as f:
            pickle.dump(vectors, f)
    
    def add_case(self, case_document: CaseDocument, vector: np.ndarray) -> None:
        """
        Add a new case to the repository with validation.
        
        Args:
            case_document: Case document to add
            vector: TF-IDF vector for the case
            
        Raises:
            ValueError: If case data is invalid or case already exists
        """
        # Load existing metadata
        cases_metadata = self.load_case_metadata()
        
        # Check repository capacity
        if len(cases_metadata) >= self.MAX_REPOSITORY_SIZE:
            raise ValueError(f"Repository capacity exceeded: cannot add more than {self.MAX_REPOSITORY_SIZE} cases")
        
        # Check if case already exists
        existing_case = next(
            (case for case in cases_metadata if case['case_id'] == case_document.case_id),
            None
        )
        
        if existing_case:
            raise ValueError(f"Case with ID {case_document.case_id} already exists")
        
        # Create and validate case metadata
        case_dict = case_document.to_dict()
        case_dict['vector_index'] = len(cases_metadata)  # Index in vector array
        
        # Validate the case data
        case_errors = self._validate_case_metadata(case_dict)
        if case_errors:
            raise ValueError(f"Invalid case data: {'; '.join(case_errors)}")
        
        # Add new case metadata
        cases_metadata.append(case_dict)
        
        # Save updated metadata
        self.save_case_metadata(cases_metadata)
        
        # Load existing vectors and append new one
        existing_vectors = self.load_case_vectors()
        if existing_vectors is not None:
            new_vectors = np.vstack([existing_vectors, vector.reshape(1, -1)])
        else:
            new_vectors = vector.reshape(1, -1)
        
        # Save updated vectors
        self.save_case_vectors(new_vectors)
    
    def get_case_by_id(self, case_id: str) -> Optional[CaseDocument]:
        """
        Retrieve a case document by its ID.
        
        Args:
            case_id: Case identifier
            
        Returns:
            CaseDocument if found, None otherwise
        """
        cases_metadata = self.load_case_metadata()
        case_data = next(
            (case for case in cases_metadata if case['case_id'] == case_id),
            None
        )
        
        if case_data is None:
            return None
        
        # Load text content from file if it exists
        text_content = ""
        if os.path.exists(case_data['file_path']):
            try:
                # This would typically involve PDF processing
                # For now, we'll leave it empty as text extraction is handled elsewhere
                pass
            except Exception as e:
                print(f"Warning: Could not load text content for {case_id}: {e}")
        
        return CaseDocument.from_dict(case_data, text_content)
    
    def get_all_cases(self) -> List[CaseDocument]:
        """
        Retrieve all case documents from the repository.
        
        Returns:
            List of all CaseDocument objects
        """
        cases_metadata = self.load_case_metadata()
        cases = []
        
        for case_data in cases_metadata:
            case_doc = CaseDocument.from_dict(case_data)
            cases.append(case_doc)
        
        return cases
    
    def get_case_count(self) -> int:
        """
        Get the total number of cases in the repository.
        
        Returns:
            Number of cases
        """
        cases_metadata = self.load_case_metadata()
        return len(cases_metadata)
    
    def remove_case(self, case_id: str) -> bool:
        """
        Remove a case from the repository with validation.
        
        Args:
            case_id: Case identifier to remove
            
        Returns:
            True if case was removed, False if not found
        """
        cases_metadata = self.load_case_metadata()
        
        # Find case to remove
        case_to_remove = None
        remove_index = -1
        for i, case in enumerate(cases_metadata):
            if case['case_id'] == case_id:
                case_to_remove = case
                remove_index = i
                break
        
        if case_to_remove is None:
            return False
        
        # Remove from metadata
        cases_metadata.pop(remove_index)
        
        # Update vector indices for remaining cases
        for i, case in enumerate(cases_metadata):
            case['vector_index'] = i
        
        # Save updated metadata with validation
        self.save_case_metadata(cases_metadata)
        
        # Remove corresponding vector
        existing_vectors = self.load_case_vectors()
        if existing_vectors is not None and remove_index < len(existing_vectors):
            # Remove the vector at the specified index
            new_vectors = np.delete(existing_vectors, remove_index, axis=0)
            self.save_case_vectors(new_vectors)
        
        return True
    
    def validate_repository(self) -> Dict[str, Any]:
        """
        Validate the repository consistency and data integrity.
        
        Returns:
            Dictionary with validation results
        """
        results = {
            'metadata_count': 0,
            'vector_count': 0,
            'consistent': True,
            'issues': [],
            'schema_valid': True,
            'capacity_ok': True
        }
        
        try:
            # Load and validate metadata structure
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                full_metadata = json.load(f)
            
            structure_errors = self._validate_metadata_structure(full_metadata)
            if structure_errors:
                results['schema_valid'] = False
                results['consistent'] = False
                results['issues'].extend([f"Schema error: {error}" for error in structure_errors])
                return results
            
            cases_metadata = full_metadata.get("cases", [])
            results['metadata_count'] = len(cases_metadata)
            
            # Validate each case
            for i, case_data in enumerate(cases_metadata):
                case_errors = self._validate_case_metadata(case_data)
                if case_errors:
                    results['consistent'] = False
                    results['issues'].extend([f"Case {i} error: {error}" for error in case_errors])
            
            # Check repository capacity
            if len(cases_metadata) > self.MAX_REPOSITORY_SIZE:
                results['capacity_ok'] = False
                results['consistent'] = False
                results['issues'].append(
                    f"Repository capacity exceeded: {len(cases_metadata)} > {self.MAX_REPOSITORY_SIZE}"
                )
            
            # Load vectors
            vectors = self.load_case_vectors()
            results['vector_count'] = len(vectors) if vectors is not None else 0
            
            # Check if metadata and vectors are consistent
            if vectors is not None and len(cases_metadata) != len(vectors):
                results['consistent'] = False
                results['issues'].append(
                    f"Metadata count ({len(cases_metadata)}) doesn't match vector count ({len(vectors)})"
                )
            
            # Check for duplicate case IDs
            case_ids = [case['case_id'] for case in cases_metadata]
            if len(case_ids) != len(set(case_ids)):
                results['consistent'] = False
                results['issues'].append("Duplicate case IDs found")
                
                # Find duplicates
                seen = set()
                duplicates = set()
                for case_id in case_ids:
                    if case_id in seen:
                        duplicates.add(case_id)
                    seen.add(case_id)
                results['issues'].append(f"Duplicate case IDs: {', '.join(duplicates)}")
            
            # Check vector indices
            for i, case in enumerate(cases_metadata):
                expected_index = i
                actual_index = case.get('vector_index', -1)
                if actual_index != expected_index:
                    results['consistent'] = False
                    results['issues'].append(
                        f"Incorrect vector index for case {case['case_id']}: expected {expected_index}, got {actual_index}"
                    )
            
            # Validate metadata section consistency
            meta_section = full_metadata.get("metadata", {})
            if meta_section.get("total_cases", 0) != len(cases_metadata):
                results['consistent'] = False
                results['issues'].append(
                    f"Metadata total_cases ({meta_section.get('total_cases', 0)}) doesn't match actual count ({len(cases_metadata)})"
                )
            
        except FileNotFoundError:
            results['consistent'] = False
            results['issues'].append("Metadata file not found")
        except json.JSONDecodeError as e:
            results['consistent'] = False
            results['schema_valid'] = False
            results['issues'].append(f"Invalid JSON in metadata file: {e}")
        except Exception as e:
            results['consistent'] = False
            results['issues'].append(f"Error during validation: {e}")
        
        return results
    
    def get_metadata_info(self) -> Dict[str, Any]:
        """
        Get metadata information about the repository.
        
        Returns:
            Dictionary with repository metadata information
        """
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                full_metadata = json.load(f)
            
            return full_metadata.get("metadata", {})
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def update_case_metadata(self, case_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update metadata for a specific case.
        
        Args:
            case_id: Case identifier to update
            updates: Dictionary of fields to update
            
        Returns:
            True if case was updated, False if not found
            
        Raises:
            ValueError: If updated data is invalid
        """
        cases_metadata = self.load_case_metadata()
        
        # Find case to update
        case_index = -1
        for i, case in enumerate(cases_metadata):
            if case['case_id'] == case_id:
                case_index = i
                break
        
        if case_index == -1:
            return False
        
        # Apply updates
        updated_case = cases_metadata[case_index].copy()
        updated_case.update(updates)
        
        # Validate updated case
        case_errors = self._validate_case_metadata(updated_case)
        if case_errors:
            raise ValueError(f"Invalid updated case data: {'; '.join(case_errors)}")
        
        # Update the case in the list
        cases_metadata[case_index] = updated_case
        
        # Save updated metadata
        self.save_case_metadata(cases_metadata)
        
        return True
    
    def search_cases_by_metadata(self, **criteria) -> List[Dict[str, Any]]:
        """
        Search cases by metadata criteria.
        
        Args:
            **criteria: Key-value pairs to search for
            
        Returns:
            List of matching case metadata dictionaries
        """
        cases_metadata = self.load_case_metadata()
        matching_cases = []
        
        for case in cases_metadata:
            match = True
            for key, value in criteria.items():
                if key not in case or case[key] != value:
                    match = False
                    break
            
            if match:
                matching_cases.append(case)
        
        return matching_cases