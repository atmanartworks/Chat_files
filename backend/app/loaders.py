from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader  # type: ignore
import os

def load_file(path, original_filename=None):
    """
    Load file and ensure metadata includes source information for citations.
    
    Args:
        path: File path (can be temp file path)
        original_filename: Original filename from database (for proper citations)
    """
    # Use original filename if provided, otherwise use basename of path
    # This ensures citations show the correct filename, not temp file names
    filename = original_filename if original_filename else os.path.basename(path)
    
    if path.endswith(".pdf"):
        docs = PyPDFLoader(path).load()
    elif path.endswith(".txt"):
        docs = TextLoader(path).load()
    elif path.endswith(".docx"):
        docs = Docx2txtLoader(path).load()
    else:
        raise ValueError("Unsupported file")
    
    # Add source metadata to all documents for citations
    for doc in docs:
        if not hasattr(doc, 'metadata') or not doc.metadata:
            doc.metadata = {}
        
        # Add source filename (use original filename, not temp file name)
        doc.metadata['source'] = filename
        
        # Ensure page number is set (for PDFs)
        if 'page' not in doc.metadata and path.endswith(".pdf"):
            # PyPDFLoader usually adds page metadata, but ensure it exists
            doc.metadata['page'] = doc.metadata.get('page', 0)
    
    return docs
