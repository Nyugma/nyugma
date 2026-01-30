"""
PDF Processing Component for Legal Case Similarity Application

This module provides functionality to extract text from PDF documents
using PyMuPDF (fitz) library with proper validation and error handling.
"""

import fitz  # PyMuPDF
from typing import Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Handles PDF text extraction and validation for legal documents.
    
    This class provides methods to:
    - Validate PDF file format using file headers and MIME types
    - Extract text content from single and multi-page PDF documents
    - Handle errors gracefully with descriptive messages
    """
    
    def __init__(self):
        """Initialize the PDF processor."""
        self.pdf_signatures = [
            b'%PDF-1.0',
            b'%PDF-1.1', 
            b'%PDF-1.2',
            b'%PDF-1.3',
            b'%PDF-1.4',
            b'%PDF-1.5',
            b'%PDF-1.6',
            b'%PDF-1.7',
            b'%PDF-2.0'
        ]
    
    def validate_pdf(self, file_content: bytes) -> bool:
        """
        Validate if the provided content is a valid PDF file.
        
        Uses file header inspection and PyMuPDF validation
        to ensure the file is actually a PDF document.
        
        Args:
            file_content (bytes): Raw file content to validate
            
        Returns:
            bool: True if valid PDF, False otherwise
            
        Requirements: 1.2 - Non-PDF file rejection
        """
        try:
            # Check PDF file header (PDF files start with %PDF-)
            if not file_content.startswith(b'%PDF-'):
                logger.warning("File does not have valid PDF header")
                return False
            
            # Check for specific PDF version signatures
            has_valid_signature = any(
                file_content.startswith(sig) for sig in self.pdf_signatures
            )
            
            if not has_valid_signature:
                logger.warning("File has PDF header but invalid version signature")
                return False
            
            # Try to open with PyMuPDF as final validation
            try:
                doc = fitz.open(stream=file_content, filetype="pdf")
                doc.close()
                return True
            except Exception as e:
                logger.warning(f"PyMuPDF validation failed: {e}")
                return False
                
        except Exception as e:
            logger.error(f"PDF validation error: {e}")
            return False
    
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file.
        
        Handles multi-page documents by concatenating text from all pages.
        Provides proper error handling for corrupted or invalid PDFs.
        
        Args:
            pdf_path (str): Path to the PDF file to process
            
        Returns:
            str: Extracted text content from the PDF
            
        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If the file is not a valid PDF or text extraction fails
            
        Requirements: 1.1 - PDF text extraction, 1.3 - Error handling
        """
        try:
            # Check if file exists
            if not Path(pdf_path).exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            # Read file content for validation
            with open(pdf_path, 'rb') as file:
                file_content = file.read()
            
            # Validate PDF format
            if not self.validate_pdf(file_content):
                raise ValueError(f"Invalid PDF file format: {pdf_path}")
            
            # Open PDF document
            doc = fitz.open(pdf_path)
            
            try:
                if doc.page_count == 0:
                    raise ValueError("PDF document contains no pages")
                
                # Extract text from all pages
                extracted_text = []
                
                for page_num in range(doc.page_count):
                    try:
                        page = doc[page_num]
                        page_text = page.get_text()
                        
                        # Add page text if not empty
                        if page_text.strip():
                            extracted_text.append(page_text)
                            
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                        continue
                
                # Concatenate all page text with newlines
                full_text = '\n'.join(extracted_text)
                
                if not full_text.strip():
                    raise ValueError("No text content could be extracted from the PDF")
                
                logger.info(f"Successfully extracted {len(full_text)} characters from {doc.page_count} pages")
                return full_text
                
            finally:
                doc.close()
            
        except (FileNotFoundError, ValueError):
            # Re-raise these as they have specific handling requirements
            raise
        except Exception as e:
            # Handle any other unexpected errors
            error_msg = f"Failed to extract text from PDF {pdf_path}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def extract_text_from_bytes(self, file_content: bytes, filename: str = "document.pdf") -> str:
        """
        Extract text content from PDF file content in memory.
        
        Useful for processing uploaded files without saving to disk first.
        
        Args:
            file_content (bytes): Raw PDF file content
            filename (str): Optional filename for logging purposes
            
        Returns:
            str: Extracted text content from the PDF
            
        Raises:
            ValueError: If the content is not a valid PDF or text extraction fails
            
        Requirements: 1.1 - PDF text extraction, 1.2 - Format validation
        """
        try:
            # Validate PDF format
            if not self.validate_pdf(file_content):
                raise ValueError(f"Invalid PDF file format: {filename}")
            
            # Open PDF from memory
            doc = fitz.open(stream=file_content, filetype="pdf")
            
            try:
                if doc.page_count == 0:
                    raise ValueError("PDF document contains no pages")
                
                # Extract text from all pages
                extracted_text = []
                
                for page_num in range(doc.page_count):
                    try:
                        page = doc[page_num]
                        page_text = page.get_text()
                        
                        # Add page text if not empty
                        if page_text.strip():
                            extracted_text.append(page_text)
                            
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num + 1} in {filename}: {e}")
                        continue
                
                # Concatenate all page text with newlines
                full_text = '\n'.join(extracted_text)
                
                if not full_text.strip():
                    raise ValueError("No text content could be extracted from the PDF")
                
                logger.info(f"Successfully extracted {len(full_text)} characters from {doc.page_count} pages in {filename}")
                return full_text
                
            finally:
                doc.close()
            
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            # Handle any other unexpected errors
            error_msg = f"Failed to extract text from PDF {filename}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)