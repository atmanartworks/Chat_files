"""Helper function to load files from Supabase Storage or local filesystem."""
import os
import tempfile
from typing import List
from .loaders import load_file
from .database import Document

def load_document_content(doc) -> List:
    """
    Load document content from Supabase Storage or local filesystem.
    
    Args:
        doc: Document database object (SQLAlchemy) or dict (Supabase)
        
    Returns:
        List of document chunks with correct source metadata
    """
    use_supabase = os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY")
    
    # Handle both dict (Supabase) and object (SQLAlchemy) types
    if isinstance(doc, dict):
        supabase_path = doc.get("supabase_path")
        filepath = doc.get("filepath")
        file_type = doc.get("file_type")
        filename = doc.get("filename")  # Original filename from database
    else:
        supabase_path = getattr(doc, 'supabase_path', None)
        filepath = getattr(doc, 'filepath', None)
        file_type = getattr(doc, 'file_type', None)
        filename = getattr(doc, 'filename', None)  # Original filename from database
    
    # Get original filename for metadata (important for citations)
    original_filename = filename or (os.path.basename(filepath) if filepath else "unknown")
    
    if use_supabase and supabase_path:
        # Download from Supabase Storage
        from .supabase_storage import download_file_from_supabase
        try:
            file_content = download_file_from_supabase(supabase_path)
            suffix = f".{file_type}" if file_type else ""
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name
            # Load file and update metadata with original filename
            docs = load_file(tmp_file_path, original_filename=original_filename)
            os.unlink(tmp_file_path)  # Clean up
            return docs
        except Exception as e:
            print(f"Error loading from Supabase Storage: {e}, trying local path...")
            # Fallback to local path if Supabase fails
            if filepath and os.path.exists(filepath):
                return load_file(filepath, original_filename=original_filename)
            raise
    elif filepath and os.path.exists(filepath):
        # Use local file
        return load_file(filepath, original_filename=original_filename)
    else:
        file_display = filename or filepath or "unknown"
        raise FileNotFoundError(f"File not found: {file_display}")

def load_file_by_path(filepath: str, file_type: str = None) -> List:
    """
    Load file by path (for legacy endpoints).
    
    Args:
        filepath: File path (local or Supabase storage path)
        file_type: Optional file type
        
    Returns:
        List of document chunks
    """
    # For legacy endpoints, assume local file
    if os.path.exists(filepath):
        return load_file(filepath)
    else:
        raise FileNotFoundError(f"File not found: {filepath}")
