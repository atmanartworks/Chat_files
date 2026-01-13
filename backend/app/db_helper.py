"""Unified database helper that works with both Supabase and SQLAlchemy."""
from typing import Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from .database import Document, ChatHistory, User
import os

def get_user_id(current_user: Any) -> int:
    """Extract user ID from current_user (works with both User object and dict)."""
    if isinstance(current_user, dict):
        return current_user.get('id')
    return getattr(current_user, 'id', None)

def is_using_supabase() -> bool:
    """Check if using Supabase."""
    return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"))

def get_user_documents(user_id: int, db: Optional[Session] = None) -> List[Union[Document, Dict]]:
    """Get all documents for a user."""
    if is_using_supabase():
        from .supabase_db import get_user_documents as supabase_get_docs
        return supabase_get_docs(user_id)
    else:
        if db:
            return db.query(Document).filter(Document.user_id == user_id).order_by(Document.uploaded_at.desc()).all()
        return []

def get_processed_documents(user_id: int, db: Optional[Session] = None) -> List[Union[Document, Dict]]:
    """Get all processed documents for a user."""
    if is_using_supabase():
        from .supabase_db import get_processed_documents as supabase_get_processed
        return supabase_get_processed(user_id)
    else:
        if db:
            return db.query(Document).filter(Document.user_id == user_id, Document.processed == True).all()
        return []

def get_document_by_id(document_id: int, user_id: int, db: Optional[Session] = None) -> Optional[Union[Document, Dict]]:
    """Get document by ID."""
    if is_using_supabase():
        from .supabase_db import get_document_by_id as supabase_get_doc
        return supabase_get_doc(document_id, user_id)
    else:
        if db:
            return db.query(Document).filter(Document.id == document_id, Document.user_id == user_id).first()
        return None

def create_chat_history_entry(user_id: int, query: str, response: str, mode: str = "rag",
                              pdf_generated: bool = False, pdf_url: Optional[str] = None,
                              citations: Optional[str] = None, db: Optional[Session] = None) -> Optional[Union[ChatHistory, Dict]]:
    """Create chat history entry."""
    if is_using_supabase():
        from .supabase_db import create_chat_history
        return create_chat_history(user_id, query, response, mode, pdf_generated, pdf_url, citations)
    else:
        if db:
            chat_history = ChatHistory(
                user_id=user_id,
                query=query,
                response=response,
                mode=mode,
                pdf_generated=pdf_generated,
                pdf_url=pdf_url,
                citations=citations
            )
            db.add(chat_history)
            db.commit()
            db.refresh(chat_history)
            return chat_history
        return None

def get_chat_history_for_user(user_id: int, limit: int = 50, skip: int = 0, db: Optional[Session] = None) -> List[Union[ChatHistory, Dict]]:
    """Get chat history for user."""
    if is_using_supabase():
        from .supabase_db import get_chat_history
        return get_chat_history(user_id, limit)
    else:
        if db:
            return db.query(ChatHistory).filter(
                ChatHistory.user_id == user_id
            ).order_by(ChatHistory.created_at.desc()).offset(skip).limit(limit).all()
        return []
