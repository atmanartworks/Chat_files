"""
Migration script to transfer data from SQLite to Supabase PostgreSQL.
Run this script once to migrate your existing data.
"""
import os
import sqlite3
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")  # PostgreSQL connection string

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    exit(1)

if not DATABASE_URL:
    print("Error: DATABASE_URL (PostgreSQL) must be set in .env file")
    exit(1)

# SQLite database path
SQLITE_DB = "./chat_with_files.db"

if not os.path.exists(SQLITE_DB):
    print(f"Error: SQLite database not found at {SQLITE_DB}")
    exit(1)

print("Starting migration from SQLite to Supabase...")

# Connect to SQLite
sqlite_conn = sqlite3.connect(SQLITE_DB)
sqlite_cursor = sqlite_conn.cursor()

# Connect to Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    # Migrate Users
    print("\n1. Migrating users...")
    sqlite_cursor.execute("SELECT id, username, email, password_hash, created_at FROM users")
    users = sqlite_cursor.fetchall()
    
    for user in users:
        user_id, username, email, password_hash, created_at = user
        try:
            supabase.table("users").insert({
                "id": user_id,
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "created_at": created_at
            }).execute()
            print(f"  ✓ Migrated user: {username}")
        except Exception as e:
            print(f"  ✗ Error migrating user {username}: {e}")
    
    # Migrate Documents
    print("\n2. Migrating documents...")
    sqlite_cursor.execute("SELECT id, user_id, filename, filepath, file_type, file_size, uploaded_at, processed FROM documents")
    documents = sqlite_cursor.fetchall()
    
    for doc in documents:
        doc_id, user_id, filename, filepath, file_type, file_size, uploaded_at, processed = doc
        try:
            # Upload file to Supabase Storage if it exists locally
            supabase_path = None
            if os.path.exists(filepath):
                try:
                    from app.supabase_storage import upload_file_to_supabase
                    with open(filepath, "rb") as f:
                        file_content = f.read()
                    supabase_path = upload_file_to_supabase(user_id, file_content, filename)
                    print(f"  ✓ Uploaded file to Supabase Storage: {filename}")
                except Exception as e:
                    print(f"  ⚠ Could not upload file {filename} to Supabase Storage: {e}")
            
            supabase.table("documents").insert({
                "id": doc_id,
                "user_id": user_id,
                "filename": filename,
                "filepath": filepath,  # Keep original path for reference
                "file_type": file_type,
                "file_size": file_size or 0,
                "uploaded_at": uploaded_at,
                "processed": bool(processed),
                "supabase_path": supabase_path
            }).execute()
            print(f"  ✓ Migrated document: {filename}")
        except Exception as e:
            print(f"  ✗ Error migrating document {filename}: {e}")
    
    # Migrate Chat History
    print("\n3. Migrating chat history...")
    sqlite_cursor.execute("SELECT id, user_id, query, response, mode, pdf_generated, pdf_url, citations, created_at FROM chat_history")
    chat_histories = sqlite_cursor.fetchall()
    
    for chat in chat_histories:
        chat_id, user_id, query, response, mode, pdf_generated, pdf_url, citations, created_at = chat
        try:
            supabase.table("chat_history").insert({
                "id": chat_id,
                "user_id": user_id,
                "query": query,
                "response": response,
                "mode": mode or "rag",
                "pdf_generated": bool(pdf_generated),
                "pdf_url": pdf_url,
                "citations": citations,
                "created_at": created_at
            }).execute()
            print(f"  ✓ Migrated chat history entry {chat_id}")
        except Exception as e:
            print(f"  ✗ Error migrating chat history {chat_id}: {e}")
    
    # Migrate Keyword Searches
    print("\n4. Migrating keyword searches...")
    sqlite_cursor.execute("SELECT id, document_id, keyword, occurrences, locations, searched_at FROM keyword_searches")
    keyword_searches = sqlite_cursor.fetchall()
    
    for search in keyword_searches:
        search_id, document_id, keyword, occurrences, locations, searched_at = search
        try:
            supabase.table("keyword_searches").insert({
                "id": search_id,
                "document_id": document_id,
                "keyword": keyword,
                "occurrences": occurrences or 0,
                "locations": locations,
                "searched_at": searched_at
            }).execute()
            print(f"  ✓ Migrated keyword search {search_id}")
        except Exception as e:
            print(f"  ✗ Error migrating keyword search {search_id}: {e}")
    
    print("\n✅ Migration completed successfully!")
    print("\nNext steps:")
    print("1. Update your .env file with DATABASE_URL pointing to Supabase PostgreSQL")
    print("2. Restart your server")
    print("3. Test the application to ensure everything works")
    
except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    sqlite_conn.close()
