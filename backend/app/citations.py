"""
Module for handling citations and source references.
"""
from typing import List, Dict, Any
from langchain_core.documents import Document

def extract_citations(documents: List[Document], current_filename: str = None) -> List[Dict[str, Any]]:
    """
    Extract citation information from retrieved documents.
    
    Args:
        documents: List of Document objects from retrieval
        current_filename: Name of the current document
    
    Returns:
        List of citation dictionaries with page numbers and sources
    """
    citations = []
    seen_sources = set()
    
    for i, doc in enumerate(documents):
        # Extract metadata
        metadata = doc.metadata if hasattr(doc, 'metadata') else {}
        page = metadata.get('page', None)
        source = metadata.get('source', current_filename or 'Document')
        
        # Create citation key (page + source)
        citation_key = f"{source}:{page}" if page else source
        
        # Avoid duplicates
        if citation_key not in seen_sources:
            seen_sources.add(citation_key)
            
            citation = {
                "id": len(citations) + 1,
                "source": source,
                "page": page,
                "snippet": doc.page_content[:200] if hasattr(doc, 'page_content') else "",  # First 200 chars
                "full_content": doc.page_content if hasattr(doc, 'page_content') else ""
            }
            citations.append(citation)
    
    return citations

def format_citations(citations: List[Dict[str, Any]]) -> str:
    """
    Format citations as a readable string.
    
    Args:
        citations: List of citation dictionaries
    
    Returns:
        Formatted citation string
    """
    if not citations:
        return ""
    
    citation_text = "\n\n**Sources:**\n"
    
    for citation in citations:
        source = citation.get('source', 'Document')
        page = citation.get('page')
        
        if page:
            citation_text += f"[{citation['id']}] {source}, Page {page}\n"
        else:
            citation_text += f"[{citation['id']}] {source}\n"
    
    return citation_text

def format_citations_inline(citations: List[Dict[str, Any]], answer: str) -> str:
    """
    Add inline citations to the answer text (ChatGPT style).
    If answer already has citations, just add sources at the end.
    
    Args:
        citations: List of citation dictionaries
        answer: The answer text
    
    Returns:
        Answer text with inline citations and sources list
    """
    if not citations:
        return answer
    
    # Check if answer already has citation numbers
    import re
    has_citations = re.search(r'\[\d+\]', answer)
    
    if not has_citations:
        # If no citations in answer, we'll let the LLM handle it
        # But add sources at the end
        citation_text = format_citations(citations)
        return answer + citation_text
    
    # Answer already has citations, just add sources list at the end
    citation_text = "\n\n**Sources:**\n"
    for citation in citations:
        source = citation.get('source', 'Document')
        page = citation.get('page')
        if page is not None:
            citation_text += f"[{citation['id']}] {source}, Page {page}\n"
        else:
            citation_text += f"[{citation['id']}] {source}\n"
    
    return answer + citation_text

def get_citation_references(citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Get simplified citation references for API response.
    
    Args:
        citations: List of citation dictionaries
    
    Returns:
        Simplified citation list for JSON response
    """
    return [
        {
            "id": cit["id"],
            "source": cit["source"],
            "page": cit.get("page"),
            "snippet": cit.get("snippet", "")[:100]  # First 100 chars
        }
        for cit in citations
    ]
