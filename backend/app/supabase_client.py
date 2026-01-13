"""Supabase client configuration."""
from supabase import create_client, Client  # type: ignore
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")  # Service role key for admin operations

def get_supabase_client() -> Client:
    """Get Supabase client instance (uses anon key by default)."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_KEY must be set in environment variables. "
            "Get them from your Supabase project settings."
        )
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_admin_client() -> Client:
    """Get Supabase admin client instance (uses service role key for admin operations like bucket creation)."""
    if not SUPABASE_URL:
        raise ValueError("SUPABASE_URL must be set in environment variables.")
    
    # Use service role key if available, otherwise fallback to anon key
    key = SUPABASE_SERVICE_KEY if SUPABASE_SERVICE_KEY else SUPABASE_KEY
    if not key:
        raise ValueError(
            "SUPABASE_SERVICE_KEY or SUPABASE_KEY must be set for admin operations. "
            "Service role key is required for bucket creation."
        )
    return create_client(SUPABASE_URL, key)

def get_storage_bucket_name(user_id: int) -> str:
    """Get storage bucket name for user."""
    return f"user-{user_id}-files"
