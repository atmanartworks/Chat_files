"""Supabase Storage helper functions for file operations."""
import os
from typing import Optional, BinaryIO
from .supabase_client import get_supabase_client, get_supabase_admin_client, get_storage_bucket_name

def upload_file_to_supabase(user_id: int, file_content: bytes, filename: str) -> str:
    """
    Upload file to Supabase Storage.
    
    Args:
        user_id: User ID
        file_content: File content as bytes
        filename: Original filename
        
    Returns:
        Storage path (bucket/path)
    """
    try:
        supabase = get_supabase_client()
        bucket_name = get_storage_bucket_name(user_id)
        
        # Ensure bucket exists (create if not exists)
        # Note: Bucket creation requires service role key, not anon key
        try:
            # Try to use admin client for bucket operations
            admin_client = get_supabase_admin_client()
            
            # Try to list buckets to check if it exists
            try:
                buckets_response = admin_client.storage.list_buckets()
                bucket_exists = False
                
                # Check if bucket exists in the list
                if hasattr(buckets_response, 'data'):
                    buckets = buckets_response.data if isinstance(buckets_response.data, list) else []
                    bucket_exists = any(bucket.get('name') == bucket_name or bucket.get('id') == bucket_name for bucket in buckets)
                elif isinstance(buckets_response, list):
                    bucket_exists = any(bucket.name == bucket_name if hasattr(bucket, 'name') else bucket.get('name') == bucket_name for bucket in buckets_response)
                
                if not bucket_exists:
                    # Create bucket if it doesn't exist (requires service role key)
                    try:
                        # Supabase Storage API: create_bucket(id, name, public=False)
                        # Try the correct API signature
                        admin_client.storage.create_bucket(
                            id=bucket_name,
                            name=bucket_name
                        )
                        print(f"Created storage bucket: {bucket_name}")
                    except Exception as create_error:
                        error_msg = str(create_error)
                        if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower() or "409" in error_msg:
                            print(f"Bucket {bucket_name} already exists")
                        else:
                            # Try alternative API signature (just bucket name)
                            try:
                                admin_client.storage.create_bucket(bucket_name)
                                print(f"Created storage bucket: {bucket_name}")
                            except Exception as alt_error:
                                print(f"Error creating bucket {bucket_name}: {create_error}")
                                print("Note: Bucket creation requires SUPABASE_SERVICE_KEY. Create bucket manually in Supabase Dashboard.")
                                raise
                else:
                    print(f"Storage bucket already exists: {bucket_name}")
            except Exception as list_error:
                # If listing fails, try to create anyway
                try:
                    # Try with id and name parameters
                    admin_client.storage.create_bucket(
                        id=bucket_name,
                        name=bucket_name
                    )
                    print(f"Created storage bucket: {bucket_name}")
                except Exception as create_error:
                    # Try alternative API signature (just bucket name)
                    try:
                        admin_client.storage.create_bucket(bucket_name)
                        print(f"Created storage bucket: {bucket_name}")
                    except Exception as alt_error:
                        error_msg = str(alt_error)
                        if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower() or "409" in error_msg:
                            print(f"Bucket {bucket_name} already exists")
                        else:
                            print(f"Warning: Could not create bucket {bucket_name}: {alt_error}")
                            print("Note: Create bucket manually in Supabase Dashboard (Storage → Buckets → New bucket)")
                            raise
        except ValueError as ve:
            # Service role key not available - provide helpful error
            print(f"Warning: {ve}")
            print(f"Bucket {bucket_name} may not exist. Please create it manually in Supabase Dashboard:")
            print(f"  1. Go to Storage → Buckets")
            print(f"  2. Click 'New bucket'")
            print(f"  3. Name: {bucket_name}")
            print(f"  4. Select 'Private'")
            print(f"  5. Click 'Create bucket'")
            print("\nOR add SUPABASE_SERVICE_KEY to .env for automatic bucket creation.")
            raise Exception(f"Bucket {bucket_name} not found. Please create it manually in Supabase Dashboard or add SUPABASE_SERVICE_KEY to .env file.")
        
        # Upload file using admin client to bypass RLS (since we use custom auth)
        # Handle duplicate files by adding timestamp to filename
        import time
        from pathlib import Path
        
        # Extract filename and extension
        file_path_obj = Path(filename)
        base_name = file_path_obj.stem
        extension = file_path_obj.suffix
        
        # Create unique filename with timestamp to avoid duplicates
        timestamp = int(time.time() * 1000)  # milliseconds for uniqueness
        unique_filename = f"{base_name}_{timestamp}{extension}"
        storage_path = f"{user_id}/{unique_filename}"
        
        admin_client = get_supabase_admin_client()
        
        # Try to upload, if duplicate error, try with different timestamp
        max_retries = 3
        for attempt in range(max_retries):
            try:
                admin_client.storage.from_(bucket_name).upload(
                    path=storage_path,
                    file=file_content,
                    file_options={"content-type": _get_content_type(filename)}
                )
                break  # Success, exit loop
            except Exception as upload_error:
                error_msg = str(upload_error)
                # Check if it's a duplicate error
                if "409" in error_msg or "duplicate" in error_msg.lower() or "already exists" in error_msg.lower():
                    if attempt < max_retries - 1:
                        # Try again with new timestamp
                        timestamp = int(time.time() * 1000) + attempt
                        unique_filename = f"{base_name}_{timestamp}{extension}"
                        storage_path = f"{user_id}/{unique_filename}"
                        continue
                    else:
                        # Last attempt failed, raise error
                        raise Exception(f"Failed to upload file after {max_retries} attempts due to duplicate conflicts")
                else:
                    # Different error, raise immediately
                    raise
        
        return f"{bucket_name}/{storage_path}"
    except Exception as e:
        print(f"Error uploading to Supabase Storage: {e}")
        raise

def download_file_from_supabase(storage_path: str) -> bytes:
    """
    Download file from Supabase Storage.
    
    Args:
        storage_path: Full storage path (bucket/path)
        
    Returns:
        File content as bytes
    """
    try:
        # Use admin client to bypass RLS (since we use custom auth)
        admin_client = get_supabase_admin_client()
        bucket_name, file_path = storage_path.split("/", 1)
        
        response = admin_client.storage.from_(bucket_name).download(file_path)
        return response
    except Exception as e:
        print(f"Error downloading from Supabase Storage: {e}")
        raise

def delete_file_from_supabase(storage_path: str) -> bool:
    """
    Delete file from Supabase Storage.
    
    Args:
        storage_path: Full storage path (bucket/path)
        
    Returns:
        True if successful
    """
    try:
        # Use admin client to bypass RLS (since we use custom auth)
        admin_client = get_supabase_admin_client()
        bucket_name, file_path = storage_path.split("/", 1)
        
        admin_client.storage.from_(bucket_name).remove([file_path])
        return True
    except Exception as e:
        print(f"Error deleting from Supabase Storage: {e}")
        return False

def get_file_url(storage_path: str, expires_in: int = 3600) -> str:
    """
    Get public URL for file (signed URL for private buckets).
    
    Args:
        storage_path: Full storage path (bucket/path)
        expires_in: URL expiration time in seconds
        
    Returns:
        Signed URL
    """
    try:
        supabase = get_supabase_client()
        bucket_name, file_path = storage_path.split("/", 1)
        
        response = supabase.storage.from_(bucket_name).create_signed_url(
            path=file_path,
            expires_in=expires_in
        )
        return response.get("signedURL", "")
    except Exception as e:
        print(f"Error getting file URL: {e}")
        return ""

def _get_content_type(filename: str) -> str:
    """Get content type from filename."""
    ext = filename.lower().split(".")[-1]
    content_types = {
        "pdf": "application/pdf",
        "txt": "text/plain",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "doc": "application/msword",
    }
    return content_types.get(ext, "application/octet-stream")
