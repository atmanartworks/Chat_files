"""Supabase database operations using Supabase client (PostgREST API)."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from .supabase_client import get_supabase_client
import os
import bcrypt

def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user by username using Supabase."""
    try:
        supabase = get_supabase_client()
        result = supabase.table("users").select("*").eq("username", username).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        error_msg = str(e)
        print(f"Error getting user by username: {error_msg}")
        # Check if table doesn't exist
        if "relation" in error_msg.lower() and "does not exist" in error_msg.lower():
            print("ERROR: 'users' table does not exist in Supabase!")
            print("Please run the SQL script from SUPABASE_ONLY_MIGRATION.md in Supabase SQL Editor")
        # Check if RLS is blocking
        if "row-level security" in error_msg.lower() or "policy" in error_msg.lower():
            print("ERROR: RLS policies are blocking access to 'users' table!")
            print("Please disable RLS or add policies for the 'users' table")
        return None

def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email using Supabase."""
    try:
        supabase = get_supabase_client()
        result = supabase.table("users").select("*").eq("email", email).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID using Supabase."""
    try:
        supabase = get_supabase_client()
        result = supabase.table("users").select("*").eq("id", user_id).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error getting user by ID: {e}")
        return None

def create_user(username: str, email: str, password: str) -> Optional[Dict]:
    """Create a new user using Supabase."""
    try:
        # Hash password
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
        
        supabase = get_supabase_client()
        result = supabase.table("users").insert({
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        error_msg = str(e)
        print(f"Error creating user: {error_msg}")
        # Check if table doesn't exist
        if "relation" in error_msg.lower() and "does not exist" in error_msg.lower():
            raise Exception("'users' table does not exist in Supabase! Please run the SQL script from SUPABASE_ONLY_MIGRATION.md in Supabase SQL Editor")
        # Check if RLS is blocking
        if "row-level security" in error_msg.lower() or "policy" in error_msg.lower() or "violates row-level security" in error_msg.lower():
            raise Exception("RLS policies are blocking user creation! Please disable RLS on 'users' table or add INSERT policy. Go to Supabase Dashboard → Authentication → Policies → users table → Disable RLS or add policy.")
        raise

def create_chat_history(user_id: int, query: str, response: str, mode: str = "rag", 
                       pdf_generated: bool = False, pdf_url: Optional[str] = None,
                       citations: Optional[str] = None) -> Optional[Dict]:
    """Create chat history entry using Supabase."""
    try:
        supabase = get_supabase_client()
        result = supabase.table("chat_history").insert({
            "user_id": user_id,
            "query": query,
            "response": response,
            "mode": mode,
            "pdf_generated": pdf_generated,
            "pdf_url": pdf_url,
            "citations": citations,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error creating chat history: {e}")
        raise

def get_chat_history(user_id: int, limit: int = 50) -> List[Dict]:
    """Get chat history for user using Supabase."""
    try:
        supabase = get_supabase_client()
        result = supabase.table("chat_history").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error getting chat history: {e}")
        return []

def create_document(user_id: int, filename: str, filepath: str, file_type: str,
                   file_size: int = 0, supabase_path: Optional[str] = None,
                   processed: bool = False) -> Optional[Dict]:
    """Create document entry using Supabase."""
    try:
        supabase = get_supabase_client()
        # Build insert data, only include supabase_path if it's not None
        insert_data = {
            "user_id": user_id,
            "filename": filename,
            "filepath": filepath,
            "file_type": file_type,
            "file_size": file_size,
            "processed": processed,
            "uploaded_at": datetime.utcnow().isoformat()
        }
        # Only add supabase_path if column exists and value is provided
        if supabase_path is not None:
            insert_data["supabase_path"] = supabase_path
        
        result = supabase.table("documents").insert(insert_data).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error creating document: {e}")
        raise

def get_user_documents(user_id: int) -> List[Dict]:
    """Get all documents for user using Supabase."""
    try:
        supabase = get_supabase_client()
        result = supabase.table("documents").select("*").eq("user_id", user_id).order("uploaded_at", desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error getting user documents: {e}")
        return []

def get_document_by_id(document_id: int, user_id: int) -> Optional[Dict]:
    """Get document by ID for specific user using Supabase."""
    try:
        supabase = get_supabase_client()
        result = supabase.table("documents").select("*").eq("id", document_id).eq("user_id", user_id).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error getting document: {e}")
        return None

def update_document(document_id: int, user_id: int, **kwargs) -> Optional[Dict]:
    """Update document using Supabase."""
    try:
        supabase = get_supabase_client()
        result = supabase.table("documents").update(kwargs).eq("id", document_id).eq("user_id", user_id).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error updating document: {e}")
        raise

def delete_document(document_id: int, user_id: int) -> bool:
    """Delete document using Supabase."""
    try:
        supabase = get_supabase_client()
        supabase.table("documents").delete().eq("id", document_id).eq("user_id", user_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting document: {e}")
        return False

def get_processed_documents(user_id: int) -> List[Dict]:
    """Get all processed documents for user using Supabase."""
    try:
        supabase = get_supabase_client()
        result = supabase.table("documents").select("*").eq("user_id", user_id).eq("processed", True).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error getting processed documents: {e}")
        return []

def check_password_hash(password_hash: str, password: str) -> bool:
    """Check if password matches hash."""
    try:
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        hash_bytes = password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception:
        return False
