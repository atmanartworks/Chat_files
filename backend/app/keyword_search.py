"""
Module to search for keywords in uploaded documents.
"""
from typing import List, Dict, Tuple
import re
from .loaders import load_file

def search_keyword_in_document(filepath: str, keyword: str) -> Dict:
    """
    Search for a keyword in a document and return occurrences with context.
    
    Args:
        filepath: Path to the document file
        keyword: Keyword to search for
    
    Returns:
        Dictionary with search results including:
        - occurrences: Number of times keyword appears
        - locations: List of locations with context
        - pages: Page numbers (for PDFs)
    """
    try:
        # Load document
        docs = load_file(filepath)
        
        keyword_lower = keyword.lower()
        occurrences = 0
        locations = []
        pages = []
        
        # Search through all document chunks
        for i, doc in enumerate(docs):
            content = doc.page_content.lower()
            page_num = doc.metadata.get('page', i + 1) if hasattr(doc, 'metadata') else i + 1
            
            # Find all occurrences (case-insensitive)
            matches = list(re.finditer(re.escape(keyword_lower), content, re.IGNORECASE))
            
            for match in matches:
                occurrences += 1
                start = max(0, match.start() - 50)  # 50 chars before
                end = min(len(doc.page_content), match.end() + 50)  # 50 chars after
                
                context = doc.page_content[start:end]
                original_context = doc.page_content[start:end]
                
                # Find the actual keyword in original case
                original_keyword = original_context[match.start() - start:match.end() - start]
                
                # Highlight keyword in context with HTML-like tags for frontend
                highlighted_context = original_context.replace(
                    original_keyword, f"<mark>{original_keyword}</mark>"
                )
                
                # Also create markdown version
                markdown_context = original_context.replace(
                    original_keyword, f"**{original_keyword}**"
                )
                
                locations.append({
                    "page": page_num,
                    "position": match.start(),
                    "context": highlighted_context.strip(),
                    "markdown_context": markdown_context.strip(),
                    "snippet": original_context.strip(),
                    "keyword_found": original_keyword
                })
                
                if page_num not in pages:
                    pages.append(page_num)
        
        return {
            "keyword": keyword,
            "occurrences": occurrences,
            "locations": locations,
            "pages": sorted(pages),
            "found": occurrences > 0
        }
    
    except Exception as e:
        return {
            "keyword": keyword,
            "occurrences": 0,
            "locations": [],
            "pages": [],
            "found": False,
            "error": str(e)
        }

def search_multiple_keywords(filepath: str, keywords: List[str]) -> Dict:
    """
    Search for multiple keywords in a document.
    
    Args:
        filepath: Path to the document
        keywords: List of keywords to search
    
    Returns:
        Dictionary with results for each keyword
    """
    results = {}
    for keyword in keywords:
        results[keyword] = search_keyword_in_document(filepath, keyword)
    
    return results
