from fastapi import FastAPI, UploadFile, File, HTTPException, Depends  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
import shutil
import os
import json
import asyncio
import re
from typing import AsyncIterator, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .loaders import load_file
from .vectorstore import create_vectorstore
from .rag import get_qa_chain
from .generator import get_direct_generation_chain
from .pdf_generator import generate_pdf_from_text
from .database import init_db, get_db, ChatHistory, Document, KeywordSearch, User
from .auth import (
    get_current_user, authenticate_user, get_password_hash,
    create_access_token, get_user_by_username, get_user_by_email
)
from fastapi.security import OAuth2PasswordRequestForm  # type: ignore
from .keyword_search import search_keyword_in_document, search_multiple_keywords
from .citations import extract_citations, format_citations_inline, get_citation_references

# Helper function to format keyword search response
def format_keyword_search_response(search_result: dict, keyword: str) -> str:
    """Format keyword search results as a readable response."""
    if not search_result["found"]:
        return f"❌ The keyword '{keyword}' was not found in the document."
    
    occurrences = search_result["occurrences"]
    pages = search_result["pages"]
    locations = search_result["locations"]
    
    response = f"Found '{keyword}' {occurrences} time(s) in the document.\n\n"
    response += f"**Pages:** {', '.join(map(str, pages))}\n\n"
    response += f"**Locations with context:**\n\n"
    
    for i, location in enumerate(locations[:10], 1):  # Show first 10 occurrences
        response += f"**{i}. Page {location['page']}:**\n"
        response += f"   {location.get('markdown_context', location.get('context', ''))}\n\n"
    
    if occurrences > 10:
        response += f"\n... and {occurrences - 10} more occurrence(s)."
    
    return response

app = FastAPI(title="FounderGPT API", version="1.0.0")

# Initialize database on startup - make it non-blocking
@app.on_event("startup")
async def startup_event():
    """Startup event - all errors are caught to prevent app crash."""
    print("=" * 50)
    print("FounderGPT API Starting...")
    print("=" * 50)
    
    # Database initialization - don't block on errors
    try:
        init_db()
        print("Database connected and initialized!")
    except Exception as e:
        print(f"Warning: Database initialization error: {e}")
        import traceback
        traceback.print_exc()
        # Continue anyway - app can still start
    
    # Load vectorstores from Qdrant Cloud
    # Wrap entire section in try-except to prevent app crash
    try:
        from .vectorstore import load_vectorstore
        from .db_helper import is_using_supabase
        
        use_supabase = is_using_supabase()
        user_ids = []
        
        # Get user IDs - handle errors gracefully
        try:
            if use_supabase:
                # Get all users with processed documents from Supabase
                try:
                    from .supabase_client import get_supabase_client
                    supabase = get_supabase_client()
                    result = supabase.table("documents").select("user_id").eq("processed", True).execute()
                    user_ids = list(set([doc["user_id"] for doc in result.data if result.data]))
                    print(f"Found {len(user_ids)} users with processed documents in Supabase")
                except ValueError as e:
                    print(f"Warning: Supabase client initialization failed: {e}")
                    print("Continuing without loading vectorstores - app will still start")
                    user_ids = []
                except Exception as e:
                    print(f"Warning: Error connecting to Supabase: {e}")
                    import traceback
                    traceback.print_exc()
                    user_ids = []
            else:
                # Get from SQLite
                try:
                    from .database import SessionLocal
                    db = SessionLocal()
                    try:
                        users_with_docs = db.query(Document.user_id).filter(Document.processed == True).distinct().all()
                        user_ids = [user_id for (user_id,) in users_with_docs]
                        print(f"Found {len(user_ids)} users with processed documents in SQLite")
                    finally:
                        db.close()
                except Exception as e:
                    print(f"Warning: Error querying SQLite: {e}")
                    user_ids = []
        except Exception as e:
            print(f"Warning: Error getting user IDs: {e}")
            import traceback
            traceback.print_exc()
            user_ids = []
        
        # Load vectorstores for each user - handle errors per user
        for user_id in user_ids:
            try:
                # Try to load from Qdrant Cloud first
                vectorstore = load_vectorstore(user_id)
                if vectorstore:
                    USER_VECTORSTORES[user_id] = vectorstore
                    USER_QA_CHAINS[user_id] = get_qa_chain(USER_VECTORSTORES[user_id])
                    print(f"Loaded vectorstore from Qdrant Cloud for user {user_id}")
                else:
                    # If not found in Qdrant Cloud, rebuild from documents
                    try:
                        from .file_loader_helper import load_document_content
                        from .db_helper import get_processed_documents
                        user_docs = get_processed_documents(user_id, None)
                        all_docs = []
                        for doc in user_docs:
                            try:
                                docs = load_document_content(doc)
                                all_docs.extend(docs)
                            except Exception as e:
                                doc_name = doc.get("filename") if isinstance(doc, dict) else getattr(doc, 'filename', 'unknown')
                                print(f"Error loading document {doc_name} for user {user_id}: {e}")
                        if all_docs:
                            USER_VECTORSTORES[user_id] = create_vectorstore(all_docs, user_id)
                            USER_QA_CHAINS[user_id] = get_qa_chain(USER_VECTORSTORES[user_id])
                            # Save to Qdrant Cloud
                            from .vectorstore import save_vectorstore
                            save_vectorstore(USER_VECTORSTORES[user_id], user_id)
                            print(f"Rebuilt and saved vectorstore to Qdrant Cloud for user {user_id} with {len(user_docs)} documents")
                    except Exception as e:
                        print(f"Warning: Error rebuilding vectorstore for user {user_id}: {e}")
                        # Continue with next user
            except Exception as e:
                print(f"Warning: Error loading vectorstore for user {user_id}: {e}")
                # Continue with next user - don't crash the app
                continue
        
        print("Startup completed - application ready to accept requests")
    except Exception as e:
        print(f"Warning: Error during startup (vectorstore loading): {e}")
        import traceback
        traceback.print_exc()
        print("Application will continue to start - vectorstores can be loaded on demand")
    
    print("=" * 50)
    print("FounderGPT API Ready - Port binding should succeed now")
    print("=" * 50)

# Add CORS middleware - Allow all localhost origins for development and production
# Update allow_origins with your frontend URL after deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:8000",
        # Add your production frontend URL here after deployment
        # "https://your-frontend-domain.com",
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",  # Allow any localhost port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VECTORSTORE = None
QA_CHAIN = None
CURRENT_DOCUMENT = None  # Track current uploaded document

# Make VECTORSTORE accessible for citations
import sys
sys.modules[__name__].VECTORSTORE = None

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)
os.makedirs("generated_pdfs", exist_ok=True)

# Root endpoint - simple test
@app.get("/")
async def root():
    """Root endpoint to verify app is running."""
    return {
        "status": "ok",
        "message": "FounderGPT API is running",
        "service": "backend"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment verification."""
    return {
        "status": "ok",
        "message": "FounderGPT API is running",
        "service": "backend"
    }

class ChatRequest(BaseModel):
    query: str
    generate_pdf: bool = False
    use_rag: bool = True  # Use RAG (document-based) or direct generation
    stream: bool = True  # Enable streaming for ChatGPT-like response

class GeneratePdfRequest(BaseModel):
    content: str
    filename: str = None

class KeywordSearchRequest(BaseModel):
    keyword: str
    document_id: Optional[int] = None

class MultipleKeywordSearchRequest(BaseModel):
    keywords: List[str]
    document_id: Optional[int] = None

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str

# Store vectorstores per user
USER_VECTORSTORES = {}
USER_QA_CHAINS = {}

# Authentication Endpoints
@app.post("/register", response_model=dict)
async def register(user_data: UserRegister, db: Optional[Session] = Depends(get_db)):
    """Register a new user."""
    use_supabase = bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"))
    
    if use_supabase:
        from .supabase_db import create_user, get_user_by_username as supabase_get_user, get_user_by_email as supabase_get_email
        if supabase_get_user(user_data.username):
            raise HTTPException(status_code=400, detail="Username already registered")
        if supabase_get_email(user_data.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        new_user = create_user(user_data.username, user_data.email, user_data.password)
        return {"message": "User registered successfully", "user_id": new_user["id"], "username": new_user["username"]}
    else:
        if get_user_by_username(db, user_data.username):
            raise HTTPException(status_code=400, detail="Username already registered")
        if get_user_by_email(db, user_data.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "User registered successfully", "user_id": new_user.id, "username": new_user.username}

@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Optional[Session] = Depends(get_db)):
    """Login and get access token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    from datetime import timedelta
    username = getattr(user, 'username', None) or (user if isinstance(user, dict) else {}).get('username')
    user_id = getattr(user, 'id', None) or (user if isinstance(user, dict) else {}).get('id')
    access_token = create_access_token(data={"sub": username}, expires_delta=timedelta(minutes=30*24*60))
    return {"access_token": access_token, "token_type": "bearer", "user_id": user_id, "username": username}

@app.get("/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information."""
    user_id = getattr(current_user, 'id', None) or (current_user if isinstance(current_user, dict) else {}).get('id')
    username = getattr(current_user, 'username', None) or (current_user if isinstance(current_user, dict) else {}).get('username')
    email = getattr(current_user, 'email', None) or (current_user if isinstance(current_user, dict) else {}).get('email')
    return {"user_id": user_id, "username": username, "email": email}

# Vault Endpoints
@app.post("/vault/upload")
async def upload_to_vault(file: UploadFile = File(...), current_user = Depends(get_current_user), db: Optional[Session] = Depends(get_db)):
    """Upload a file to user's vault."""
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Get user ID
        user_id = getattr(current_user, 'id', None) or (current_user if isinstance(current_user, dict) else {}).get('id')
        
        # Check if using Supabase
        use_supabase = bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"))
        
        if use_supabase:
            # Upload to Supabase Storage
            from .supabase_storage import upload_file_to_supabase
            from .supabase_db import create_document
            # Get original filename for display, but storage will use unique name
            original_filename = file.filename
            storage_path = upload_file_to_supabase(user_id, file_content, original_filename)
            file_path = storage_path  # Store storage path
            supabase_path = storage_path
            # Extract the actual stored filename from storage_path
            stored_filename = storage_path.split("/")[-1] if "/" in storage_path else storage_path
            # Use original filename for database record (user sees original name)
            display_filename = original_filename
        else:
            # Fallback to local storage
            user_upload_dir = f"uploads/user_{user_id}"
            os.makedirs(user_upload_dir, exist_ok=True)
            file_path = os.path.join(user_upload_dir, file.filename)
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
            supabase_path = None
        
        file_type = "pdf" if file.filename.endswith(".pdf") else "txt" if file.filename.endswith(".txt") else "docx" if file.filename.endswith(".docx") else "unknown"
        
        if use_supabase:
            # Use original filename for display (user sees original name, not timestamped version)
            filename_for_db = display_filename if 'display_filename' in locals() else file.filename
            db_document = create_document(user_id, filename_for_db, file_path, file_type, file_size, supabase_path, False)
            document_id = db_document["id"] if db_document else None
            # Store for later use in vectorstore rebuild
            new_file_info = {
                "id": document_id,
                "filename": filename_for_db,
                "filepath": file_path,
                "file_type": file_type,
                "supabase_path": supabase_path,
                "processed": False
            }
        else:
            db_document = Document(
                user_id=user_id, 
                filename=file.filename, 
                filepath=file_path, 
                file_type=file_type, 
                file_size=file_size, 
                processed=False,
                supabase_path=supabase_path
            )
            db.add(db_document)
            db.commit()
            db.refresh(db_document)
            document_id = db_document.id
        try:
            # For processing, we need the file content
            if use_supabase:
                # Use file_content directly for processing
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as tmp_file:
                    tmp_file.write(file_content)
                    tmp_file_path = tmp_file.name
                # Pass original filename for proper metadata
                docs = load_file(tmp_file_path, original_filename=file.filename)
                os.unlink(tmp_file_path)  # Clean up temp file
            else:
                docs = load_file(file_path, original_filename=file.filename)
            if not docs or len(docs) == 0:
                raise Exception("No content extracted from file")
            
            # Always rebuild vectorstore completely to ensure correct metadata and consistency
            # This ensures deleted files are removed and new files have correct metadata
            from .vectorstore import delete_vectorstore, create_vectorstore, save_vectorstore
            from .file_loader_helper import load_document_content
            from .db_helper import get_user_documents
            
            # Get ALL documents for user (both processed and new one)
            # We need to include the new file even though it's not marked processed yet
            all_user_docs = get_user_documents(user_id, db)
            
            # Filter to get only documents that can be loaded (have supabase_path or filepath)
            all_docs_to_process = []
            for doc in all_user_docs:
                if isinstance(doc, dict):
                    has_path = doc.get("supabase_path") or doc.get("filepath")
                else:
                    has_path = getattr(doc, 'supabase_path', None) or getattr(doc, 'filepath', None)
                if has_path:
                    all_docs_to_process.append(doc)
            
            # Also add the newly uploaded file explicitly (in case it's not in the list yet)
            if use_supabase:
                new_doc = {
                    "id": document_id,
                    "filename": filename_for_db,
                    "filepath": file_path,
                    "file_type": file_type,
                    "supabase_path": supabase_path,
                    "processed": False
                }
                # Check if new file is already in the list
                new_file_in_list = any(
                    (isinstance(d, dict) and d.get("id") == document_id) or 
                    (not isinstance(d, dict) and getattr(d, 'id', None) == document_id)
                    for d in all_docs_to_process
                )
                if not new_file_in_list:
                    all_docs_to_process.append(new_doc)
            else:
                if db_document not in all_docs_to_process:
                    all_docs_to_process.append(db_document)
            
            # Load all documents with correct metadata
            all_docs = []
            for doc in all_docs_to_process:
                try:
                    filename = doc.get("filename") if isinstance(doc, dict) else getattr(doc, 'filename', 'unknown')
                    print(f"Loading document for vectorstore: {filename}")
                    loaded_docs = load_document_content(doc)
                    all_docs.extend(loaded_docs)
                    print(f"Successfully loaded {len(loaded_docs)} chunks from {filename}")
                except Exception as e:
                    filename = doc.get("filename") if isinstance(doc, dict) else getattr(doc, 'filename', 'unknown')
                    print(f"Error loading document {filename} during rebuild: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Delete old vectorstore and create fresh one
            if user_id in USER_VECTORSTORES:
                del USER_VECTORSTORES[user_id]
                del USER_QA_CHAINS[user_id]
            delete_vectorstore(user_id)
            
            # Create fresh vectorstore with all documents (including new one)
            if all_docs:
                print(f"Creating vectorstore with {len(all_docs)} total chunks from {len(all_docs_to_process)} documents")
                USER_VECTORSTORES[user_id] = create_vectorstore(all_docs, user_id)
                USER_QA_CHAINS[user_id] = get_qa_chain(USER_VECTORSTORES[user_id])
                save_vectorstore(USER_VECTORSTORES[user_id], user_id)
                print(f"Successfully rebuilt vectorstore for user {user_id} with {len(all_docs_to_process)} documents ({len(all_docs)} chunks)")
            else:
                print(f"Warning: No documents loaded for vectorstore after upload. Tried to load {len(all_docs_to_process)} documents.")
            
            # Update document as processed
            if use_supabase:
                from .supabase_db import update_document
                update_document(document_id, user_id, processed=True)
            else:
                db_document.processed = True
                db.commit()
            print(f"Successfully processed document {file.filename} for user {user_id}")
        except Exception as e:
            print(f"Error processing document: {e}")
            if use_supabase:
                from .supabase_db import update_document
                if document_id:
                    update_document(document_id, user_id, processed=False)
            else:
                db_document.processed = False
                db.commit()
            # Don't raise error, just mark as not processed
        processed = True if use_supabase else db_document.processed
        return {"message": "File uploaded to vault successfully", "document_id": document_id, "filename": file.filename, "file_size": file_size, "processed": processed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@app.get("/vault/files")
async def get_vault_files(current_user = Depends(get_current_user), db: Optional[Session] = Depends(get_db)):
    """Get all files in user's vault."""
    from .db_helper import get_user_id, get_user_documents
    user_id = get_user_id(current_user)
    documents = get_user_documents(user_id, db)
    
    # Format documents (works with both dict and object)
    files = []
    for doc in documents:
        if isinstance(doc, dict):
            files.append({
                "id": doc.get("id"),
                "filename": doc.get("filename"),
                "file_type": doc.get("file_type"),
                "file_size": doc.get("file_size") or 0,
                "uploaded_at": doc.get("uploaded_at"),
                "processed": doc.get("processed") or False
            })
        else:
            files.append({
                "id": doc.id,
                "filename": doc.filename,
                "file_type": doc.file_type,
                "file_size": doc.file_size or 0,
                "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
                "processed": doc.processed or False
            })
    
    return {
        "files": files,
        "total": len(files)
    }

@app.delete("/vault/files/{file_id}")
async def delete_vault_file(file_id: int, current_user = Depends(get_current_user), db: Optional[Session] = Depends(get_db)):
    """Delete a file from user's vault."""
    from .db_helper import get_user_id, get_document_by_id, get_processed_documents
    user_id = get_user_id(current_user)
    document = get_document_by_id(file_id, user_id, db)
    
    if not document:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Get document attributes (works with both dict and object)
    supabase_path = None
    filepath = None
    if isinstance(document, dict):
        supabase_path = document.get("supabase_path")
        filepath = document.get("filepath")
    else:
        supabase_path = getattr(document, 'supabase_path', None)
        filepath = getattr(document, 'filepath', None)
    
    # Delete from Supabase Storage if using Supabase
    use_supabase = os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY")
    if use_supabase and supabase_path:
        from .supabase_storage import delete_file_from_supabase
        delete_file_from_supabase(supabase_path)
    elif filepath and os.path.exists(filepath):
        # Fallback to local file deletion
        os.remove(filepath)
    
    # Delete from database
    if use_supabase:
        from .supabase_db import delete_document
        delete_document(file_id, user_id)
    else:
        if db and not isinstance(document, dict):
            db.delete(document)
            db.commit()
    
    # Always rebuild vectorstore after deletion to ensure old chunks are removed
    # Delete existing vectorstore first to remove all old data
    if user_id in USER_VECTORSTORES:
        del USER_VECTORSTORES[user_id]
        del USER_QA_CHAINS[user_id]
    
    # Delete collection from Qdrant to remove all old chunks
    from .vectorstore import delete_vectorstore, create_vectorstore, save_vectorstore
    delete_vectorstore(user_id)
    
    # Rebuild vectorstore with only remaining documents
    remaining_docs = get_processed_documents(user_id, db)
    if remaining_docs:
        all_docs = []
        for doc in remaining_docs:
            try:
                from .file_loader_helper import load_document_content
                docs = load_document_content(doc)
                all_docs.extend(docs)
            except Exception as e:
                filename = doc.get("filename") if isinstance(doc, dict) else getattr(doc, 'filename', 'unknown')
                print(f"Error loading document {filename} during rebuild: {e}")
        
        if all_docs:
            # Create fresh vectorstore with only remaining documents
            USER_VECTORSTORES[user_id] = create_vectorstore(all_docs, user_id)
            USER_QA_CHAINS[user_id] = get_qa_chain(USER_VECTORSTORES[user_id])
            # Save to Qdrant Cloud
            save_vectorstore(USER_VECTORSTORES[user_id], user_id)
            print(f"Rebuilt vectorstore for user {user_id} with {len(remaining_docs)} documents")
        else:
            print(f"No documents could be loaded for user {user_id} after deletion")
    else:
        print(f"No remaining documents for user {user_id}, vectorstore deleted")
    return {"message": "File deleted successfully"}

@app.post("/vault/rebuild-vectorstore")
async def rebuild_vectorstore(current_user = Depends(get_current_user), db: Optional[Session] = Depends(get_db)):
    """Rebuild vectorstore for current user with correct metadata."""
    try:
        from .db_helper import get_user_id, get_processed_documents
        from .vectorstore import delete_vectorstore, create_vectorstore, save_vectorstore
        from .file_loader_helper import load_document_content
        from .rag import get_qa_chain
        
        user_id = get_user_id(current_user)
        
        # Delete existing vectorstore from Qdrant
        try:
            delete_vectorstore(user_id)
            print(f"Deleted existing vectorstore for user {user_id}")
        except Exception as e:
            print(f"Note: Could not delete vectorstore (might not exist): {e}")
        
        # Get all processed documents for user
        user_docs = get_processed_documents(user_id, db)
        
        if not user_docs:
            return {"message": "No documents found to rebuild vectorstore", "documents_count": 0}
        
        # Rebuild vectorstore from all documents
        all_docs = []
        successful_files = []
        failed_files = []
        
        for doc in user_docs:
            try:
                docs = load_document_content(doc)
                all_docs.extend(docs)
                filename = doc.get("filename") if isinstance(doc, dict) else getattr(doc, 'filename', 'unknown')
                successful_files.append(filename)
            except Exception as e:
                filename = doc.get("filename") if isinstance(doc, dict) else getattr(doc, 'filename', 'unknown')
                failed_files.append({"filename": filename, "error": str(e)})
                print(f"Error loading document {filename}: {e}")
        
        if all_docs:
            # Create new vectorstore with correct metadata
            USER_VECTORSTORES[user_id] = create_vectorstore(all_docs, user_id)
            USER_QA_CHAINS[user_id] = get_qa_chain(USER_VECTORSTORES[user_id])
            
            # Save to Qdrant Cloud
            save_vectorstore(USER_VECTORSTORES[user_id], user_id)
            
            return {
                "message": "Vectorstore rebuilt successfully",
                "documents_processed": len(successful_files),
                "documents_failed": len(failed_files),
                "total_chunks": len(all_docs),
                "successful_files": successful_files,
                "failed_files": failed_files
            }
        else:
            return {
                "message": "No documents could be loaded",
                "documents_processed": 0,
                "documents_failed": len(failed_files),
                "failed_files": failed_files
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rebuilding vectorstore: {str(e)}")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    global VECTORSTORE, QA_CHAIN, CURRENT_DOCUMENT

    try:
        path = f"uploads/{file.filename}"
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Determine file type
        file_type = "pdf" if file.filename.endswith(".pdf") else \
                   "txt" if file.filename.endswith(".txt") else \
                   "docx" if file.filename.endswith(".docx") else "unknown"

        # Save document info to database
        db_document = Document(
            filename=file.filename,
            filepath=path,
            file_type=file_type,
            processed=False
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)

        # Process document (legacy endpoint - use user_id 0 for non-user uploads)
        docs = load_file(path)
        # Note: Legacy endpoint doesn't have user context, using user_id 0
        VECTORSTORE = create_vectorstore(docs, 0)
        QA_CHAIN = get_qa_chain(VECTORSTORE)
        CURRENT_DOCUMENT = db_document

        # Update document as processed
        db_document.processed = True
        db.commit()

        return {
            "message": "File processed successfully",
            "document_id": db_document.id,
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def stream_chain_response(chain, query: str, use_rag: bool = False, user_id: int = None):
    """Stream response from a LangChain chain - optimized for speed."""
    full_response = ""
    citations_data = []
    
    try:
        # Use astream() for async streaming with immediate flush
        async for chunk in chain.astream(query):
            if chunk:
                chunk_str = str(chunk)
                full_response += chunk_str
                # Send immediately without buffering
                yield f"data: {json.dumps({'chunk': chunk_str, 'done': False})}\n\n"
        
        # If RAG mode, get citations after streaming
        if use_rag and user_id and user_id in USER_VECTORSTORES:
            try:
                user_vectorstore = USER_VECTORSTORES[user_id]
                source_docs = user_vectorstore.similarity_search(query, k=3)
                citations = extract_citations(source_docs, None)
                citations_data = get_citation_references(citations)
            except Exception as e:
                print(f"Error getting citations: {e}")
                citations_data = []
        
        yield f"data: {json.dumps({'chunk': '', 'done': True, 'full_response': full_response, 'citations': citations_data})}\n\n"
    except Exception as e:
        error_msg = str(e)
        yield f"data: {json.dumps({'error': error_msg, 'done': True})}\n\n"

@app.post("/chat")
async def chat(request: ChatRequest, current_user = Depends(get_current_user), db: Optional[Session] = Depends(get_db)):
    try:
        # Detect greetings (hi, hello, hey) - return simple greeting + vault files
        greeting_keywords = ["hi", "hello", "hey", "hai", "namaste", "greetings"]
        query_lower = request.query.lower().strip()
        is_greeting = query_lower in greeting_keywords or query_lower in [f"{g}!" for g in greeting_keywords] or query_lower in [f"{g}." for g in greeting_keywords]
        
        if is_greeting:
            # For instant response, use streaming even for greetings
            if request.stream:
                # Stream greeting response immediately (INSTANT like ChatGPT)
                # Capture query and user_id before async function
                query_text = request.query
                user_id = getattr(current_user, 'id', None) or (current_user if isinstance(current_user, dict) else {}).get('id')
                
                async def stream_greeting():
                    # Send greeting IMMEDIATELY (no delay, no DB queries first)
                    greeting_text = "Hi! How can I help you today?"
                    yield f"data: {json.dumps({'chunk': greeting_text, 'done': False})}\n\n"
                    
                    # Get vault files AFTER sending greeting (non-blocking)
                    try:
                        from .db_helper import get_user_documents, create_chat_history_entry
                        vault_files = get_user_documents(user_id, db)
                        
                        if vault_files:
                            vault_text = "\n\n**Files in your vault:**\n"
                            for i, file in enumerate(vault_files[:10], 1):
                                file_size = file.get("file_size") if isinstance(file, dict) else getattr(file, 'file_size', 0)
                                file_size_mb = (file_size or 0) / (1024 * 1024)
                                file_size_str = f"{file_size_mb:.2f} MB" if file_size_mb > 0 else "0 MB"
                                processed = file.get("processed") if isinstance(file, dict) else getattr(file, 'processed', False)
                                status = "[PROCESSED]" if processed else "[PENDING]"
                                filename = file.get("filename") if isinstance(file, dict) else getattr(file, 'filename', '')
                                vault_text += f"{i}. {status} {filename} ({file_size_str})\n"
                            if len(vault_files) > 10:
                                vault_text += f"\n... and {len(vault_files) - 10} more files"
                            yield f"data: {json.dumps({'chunk': vault_text, 'done': False})}\n\n"
                            
                            full_response = greeting_text + vault_text
                            vault_files_data = [
                                {
                                    "id": doc.get("id") if isinstance(doc, dict) else doc.id,
                                    "filename": doc.get("filename") if isinstance(doc, dict) else doc.filename,
                                    "file_type": doc.get("file_type") if isinstance(doc, dict) else doc.file_type,
                                    "file_size": doc.get("file_size") or 0 if isinstance(doc, dict) else (doc.file_size or 0),
                                    "processed": doc.get("processed") or False if isinstance(doc, dict) else (doc.processed or False)
                                }
                                for doc in vault_files
                            ]
                        else:
                            vault_text = "\n\nYour vault is empty. Upload files to get started!"
                            yield f"data: {json.dumps({'chunk': vault_text, 'done': False})}\n\n"
                            full_response = greeting_text + vault_text
                            vault_files_data = []
                        
                        # Save to chat history (non-blocking, don't wait for commit)
                        try:
                            create_chat_history_entry(user_id, query_text, full_response, "greeting", db=db)
                        except Exception as e:
                            print(f"Error saving chat history: {e}")
                            pass  # Don't block on DB save
                        
                        yield f"data: {json.dumps({'chunk': '', 'done': True, 'full_response': full_response, 'vault_files': vault_files_data})}\n\n"
                    except Exception as e:
                        print(f"Error in greeting stream: {e}")
                        import traceback
                        traceback.print_exc()
                        yield f"data: {json.dumps({'chunk': '', 'done': True, 'full_response': greeting_text})}\n\n"
                
                return StreamingResponse(stream_greeting(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"})
            else:
                # Non-streaming fallback (shouldn't happen for greetings, but just in case)
                from .db_helper import get_user_id, get_user_documents, create_chat_history_entry
                user_id = get_user_id(current_user)
                vault_files = get_user_documents(user_id, db)
                greeting_response = "Hi! How can I help you today?"
                
                if vault_files:
                    greeting_response += "\n\n**Files in your vault:**\n"
                    for i, file in enumerate(vault_files[:10], 1):
                        file_size = file.get("file_size") if isinstance(file, dict) else getattr(file, 'file_size', 0)
                        file_size_mb = (file_size or 0) / (1024 * 1024)
                        file_size_str = f"{file_size_mb:.2f} MB" if file_size_mb > 0 else "0 MB"
                        processed = file.get("processed") if isinstance(file, dict) else getattr(file, 'processed', False)
                        status = "[PROCESSED]" if processed else "[PENDING]"
                        filename = file.get("filename") if isinstance(file, dict) else getattr(file, 'filename', '')
                        greeting_response += f"{i}. {status} {filename} ({file_size_str})\n"
                    if len(vault_files) > 10:
                        greeting_response += f"\n... and {len(vault_files) - 10} more files"
                else:
                    greeting_response += "\n\nYour vault is empty. Upload files to get started!"
                
                # Save to chat history
                create_chat_history_entry(user_id, request.query, greeting_response, "greeting", db=db)
                
                return {
                    "answer": greeting_response,
                    "mode": "greeting",
                    "vault_files": [
                        {
                            "id": doc.id,
                            "filename": doc.filename,
                            "file_type": doc.file_type,
                            "file_size": doc.file_size or 0,
                            "processed": doc.processed or False
                        }
                        for doc in vault_files
                    ]
                }
        
        # Detect if user wants keyword search (keywords like "highlight", "find", "search", "show")
        search_keywords = ["highlight", "find", "search", "show", "where is", "locate", "point out"]
        wants_search = any(keyword in request.query.lower() for keyword in search_keywords)
        
        # Extract keyword from query if it's a search request
        if wants_search and CURRENT_DOCUMENT:
            # Try to extract keyword from query (e.g., "highlight indhumathi")
            import re
            # Look for quoted words or words after search keywords
            keyword_match = re.search(r'(?:highlight|find|search|show|locate|point out)\s+["\']?(\w+)["\']?', request.query, re.IGNORECASE)
            if keyword_match:
                keyword = keyword_match.group(1)
                # Perform keyword search
                search_result = search_keyword_in_document(CURRENT_DOCUMENT.filepath, keyword)
                formatted_response = format_keyword_search_response(search_result, keyword)
                
                # Save to chat history
                chat_history = ChatHistory(
                    query=request.query,
                    response=formatted_response,
                    mode="search"
                )
                db.add(chat_history)
                db.commit()
                
                return {
                    "answer": formatted_response,
                    "mode": "search",
                    "search_results": search_result
                }
        
        # Smart mode detection:
        # 1. If user has documents, check if query is about document content
        # 2. If query mentions document content (names, entities), use RAG
        # 3. Only use generation for truly creative/unrelated queries
        
        from .db_helper import get_user_id
        user_id = get_user_id(current_user)
        use_rag = request.use_rag
        has_documents = user_id in USER_VECTORSTORES
        
        if has_documents:
            # Check if query is about document content
            try:
                user_vectorstore = USER_VECTORSTORES[user_id]
                # Quick check: search documents for relevance
                test_docs = user_vectorstore.similarity_search(request.query, k=2)
                if test_docs and len(test_docs) > 0:
                    # Check if any document content is relevant to the query
                    doc_content = " ".join([doc.page_content[:200] for doc in test_docs]).lower()
                    query_lower = request.query.lower()
                    
                    # If query mentions names/entities that appear in documents, use RAG
                    # Extract potential names/entities from query (words after "for", "about", "of")
                    import re
                    # Common words to ignore
                    common_words = {'the', 'a', 'an', 'simple', 'basic', 'new', 'old', 'good', 'best', 'quick', 'easy'}
                    
                    # Look for patterns like "for X", "about X", "X's resume", etc. (case-insensitive)
                    name_patterns = [
                        r'(?:for|about|of)\s+(?:the\s+)?([a-z]{4,})',  # "for indhumathi" (4+ chars, skip "the")
                        r'([a-z]{4,})\'s',  # "indhumathi's" (4+ chars)
                        r'([a-z]{4,})\s+(?:resume|education|experience|profile|cv)',  # "indhumathi resume" (4+ chars)
                    ]
                    
                    query_has_name = False
                    for pattern in name_patterns:
                        matches = re.findall(pattern, request.query, re.IGNORECASE)
                        if matches:
                            # Check if the matched name appears in document content
                            for match in matches:
                                match_lower = match.lower()
                                # Skip common words
                                if match_lower not in common_words and len(match) >= 4:
                                    if match_lower in doc_content:
                                        query_has_name = True
                                        print(f"Found name/entity '{match}' in documents, using RAG")
                                        break
                            if query_has_name:
                                break
                    
                    # If query has generation keywords BUT is about document content, use RAG
                    generation_keywords = ["generate", "create", "write", "make", "prepare", "draft"]
                    has_generation_keyword = any(kw in query_lower for kw in generation_keywords)
                    
                    if has_generation_keyword and query_has_name:
                        # "make resume for Indhumathi" - use RAG because Indhumathi is in docs
                        use_rag = True
                        print(f"Query is about document content, using RAG mode: {request.query}")
                    elif not has_generation_keyword:
                        # No generation keywords, use RAG if documents exist
                        use_rag = True
                    else:
                        # Has generation keywords but not clearly about document content
                        # Check if documents are highly relevant to the query
                        relevant_words = [word for word in query_lower.split() if len(word) > 3 and word not in common_words]
                        if relevant_words and any(word in doc_content for word in relevant_words):
                            use_rag = True
                            print(f"Documents are relevant to query, using RAG mode")
                        else:
                            # Not clearly about documents, allow generation mode
                            use_rag = False
                            print(f"Query seems to be creative generation, using generation mode")
            except Exception as e:
                print(f"Error checking document relevance: {e}")
                # Default to RAG if documents exist
                use_rag = request.use_rag and has_documents
        else:
            # No documents, use generation if generation keywords present
            generation_keywords = ["generate", "create", "write", "make", "prepare", "draft"]
            has_generation_keyword = any(kw in request.query.lower() for kw in generation_keywords)
            use_rag = False if has_generation_keyword else request.use_rag
        
        # If streaming is requested and not generating PDF
        if request.stream and not request.generate_pdf:
            if use_rag:
                # Load vectorstore if missing but documents exist
                if user_id not in USER_QA_CHAINS:
                    # Try to load from disk first
                    from .vectorstore import load_vectorstore, save_vectorstore
                    from .db_helper import get_processed_documents
                    vectorstore = load_vectorstore(user_id)
                    if vectorstore:
                        USER_VECTORSTORES[user_id] = vectorstore
                        USER_QA_CHAINS[user_id] = get_qa_chain(USER_VECTORSTORES[user_id])
                        print(f"Loaded vectorstore from disk for user {user_id}")
                    else:
                        # Check if user has processed documents
                        user_docs = get_processed_documents(user_id, db)
                        if user_docs:
                            # Rebuild vectorstore from existing documents
                            all_docs = []
                            for doc in user_docs:
                                try:
                                    from .file_loader_helper import load_document_content
                                    docs = load_document_content(doc)
                                    all_docs.extend(docs)
                                except Exception as e:
                                    doc_name = doc.get("filename") if isinstance(doc, dict) else getattr(doc, 'filename', 'unknown')
                                    print(f"Error loading document {doc_name}: {e}")
                            if all_docs:
                                USER_VECTORSTORES[user_id] = create_vectorstore(all_docs, user_id)
                                USER_QA_CHAINS[user_id] = get_qa_chain(USER_VECTORSTORES[user_id])
                                # Save to Qdrant Cloud
                                save_vectorstore(USER_VECTORSTORES[user_id], user_id)
                                print(f"Rebuilt and saved vectorstore for user {user_id} with {len(user_docs)} documents")
                            else:
                                raise HTTPException(status_code=400, detail="Upload files to your vault first to use document-based chat")
                        else:
                            raise HTTPException(status_code=400, detail="Upload files to your vault first to use document-based chat")
                chain = USER_QA_CHAINS[user_id]
            else:
                chain = get_direct_generation_chain()
            
            full_response_collector = []
            async def stream_and_collect():
                nonlocal full_response_collector
                async for chunk_data in stream_chain_response(chain, request.query, use_rag, user_id):
                    data = json.loads(chunk_data[6:])
                    if data.get("chunk"):
                        full_response_collector.append(data["chunk"])
                    yield chunk_data
                if full_response_collector:
                    full_response = ''.join(full_response_collector)
                    citations_data = data.get("citations", []) if data.get("done") else []
                    from .db_helper import create_chat_history_entry
                    create_chat_history_entry(user_id, request.query, full_response, "rag" if use_rag else "generation", citations=json.dumps(citations_data) if citations_data else None, db=db)
            return StreamingResponse(stream_and_collect(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"})
        
        # Non-streaming response (for PDF generation or when stream=False)
        citations = []
        citations_data = []
        
        if use_rag:
            # Use RAG (document-based Q&A) with citations - search across all user's files
            # Load vectorstore if missing but documents exist
            if user_id not in USER_VECTORSTORES:
                # Try to load from disk first
                from .vectorstore import load_vectorstore, save_vectorstore
                from .db_helper import get_processed_documents
                vectorstore = load_vectorstore(user_id)
                if vectorstore:
                    USER_VECTORSTORES[user_id] = vectorstore
                    USER_QA_CHAINS[user_id] = get_qa_chain(USER_VECTORSTORES[user_id])
                    print(f"Loaded vectorstore from disk for user {user_id}")
                else:
                    # Check if user has processed documents
                    user_docs = get_processed_documents(user_id, db)
                    if user_docs:
                        # Rebuild vectorstore from existing documents
                        all_docs = []
                        for doc in user_docs:
                            try:
                                from .file_loader_helper import load_document_content
                                docs = load_document_content(doc)
                                all_docs.extend(docs)
                            except Exception as e:
                                doc_name = doc.get("filename") if isinstance(doc, dict) else getattr(doc, 'filename', 'unknown')
                                print(f"Error loading document {doc_name}: {e}")
                        if all_docs:
                            USER_VECTORSTORES[user_id] = create_vectorstore(all_docs, user_id)
                            USER_QA_CHAINS[user_id] = get_qa_chain(USER_VECTORSTORES[user_id])
                            # Save to Qdrant Cloud
                            save_vectorstore(USER_VECTORSTORES[user_id], user_id)
                            print(f"Rebuilt and saved vectorstore for user {user_id}")
                        else:
                            raise HTTPException(status_code=400, detail="Upload files to your vault first to use document-based chat")
                    else:
                        raise HTTPException(status_code=400, detail="Upload files to your vault first to use document-based chat")
            
            user_vectorstore = USER_VECTORSTORES[user_id]
            
            # Get answer with sources for citations
            from .rag import get_answer_with_sources
            result_dict = get_answer_with_sources(user_vectorstore, request.query)
            result = result_dict["answer"]
            source_docs = result_dict.get("sources", [])
            
            # Extract citations from source documents
            citations = extract_citations(source_docs, None)  # Will use source metadata
            citations_data = get_citation_references(citations)
            
            # Add citations to answer
            result = format_citations_inline(citations, result)
        else:
            # Use direct generation (creative content) - no citations
            generation_chain = get_direct_generation_chain()
            result = generation_chain.invoke(request.query)
        
        # Prepare response data
        pdf_url = None
        pdf_generated = False
        
        # If PDF generation is requested
        if request.generate_pdf:
            pdf_path = generate_pdf_from_text(result)
            pdf_url = f"/download-pdf/{os.path.basename(pdf_path)}"
            pdf_generated = True
        
        # Save chat history to database
        from .db_helper import create_chat_history_entry
        create_chat_history_entry(
            user_id,
            request.query,
            result,
            "rag" if use_rag else "generation",
            pdf_generated,
            pdf_url,
            json.dumps(citations_data) if citations_data else None,
            db=db
        )
        
        response_data = {
            "answer": result,
            "mode": "rag" if use_rag else "generation"
        }
        
        # Add citations if available
        if citations_data:
            response_data["citations"] = citations_data
        
        if pdf_generated:
            response_data["pdf_url"] = pdf_url
            response_data["pdf_generated"] = True
        
        return response_data
    except ConnectionError as e:
        error_msg = str(e)
        if "10061" in error_msg or "actively refused" in error_msg.lower():
            raise HTTPException(
                status_code=503,
                detail="LLM service is not available. Please ensure either GROQ_API_KEY is set in your environment variables, or Ollama service is running."
            )
        raise HTTPException(status_code=503, detail=f"Connection error: {error_msg}")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/generate-pdf")
async def generate_pdf(request: GeneratePdfRequest):
    """Generate a PDF from text content."""
    try:
        pdf_path = generate_pdf_from_text(request.content, request.filename)
        return {
            "message": "PDF generated successfully",
            "filename": os.path.basename(pdf_path),
            "download_url": f"/download-pdf/{os.path.basename(pdf_path)}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@app.get("/download-pdf/{filename}")
async def download_pdf(filename: str):
    """Download a generated PDF file."""
    pdf_path = os.path.join("generated_pdfs", filename)
    
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=filename
    )

# Database endpoints
@app.get("/chat-history")
async def get_chat_history(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for current user."""
    from .db_helper import get_user_id, get_chat_history_for_user
    user_id = get_user_id(current_user)
    history = get_chat_history_for_user(user_id, limit, skip, db)
    
    # Format history (works with both dict and object)
    formatted_history = []
    for h in history:
        if isinstance(h, dict):
            formatted_history.append({
                "id": h.get("id"),
                "query": h.get("query"),
                "response": h.get("response"),
                "mode": h.get("mode"),
                "created_at": h.get("created_at"),
                "citations": json.loads(h.get("citations")) if h.get("citations") else None,
                "pdf_url": h.get("pdf_url"),
                "pdf_generated": h.get("pdf_generated") or False
            })
        else:
            formatted_history.append({
                "id": h.id,
                "query": h.query,
                "response": h.response,
                "mode": h.mode,
                "created_at": h.created_at.isoformat() if h.created_at else None,
                "citations": json.loads(h.citations) if h.citations else None,
                "pdf_url": h.pdf_url,
                "pdf_generated": h.pdf_generated or False
            })
    
    return {
        "history": formatted_history,
        "total": len(formatted_history)
    }

@app.get("/documents")
async def get_documents(db: Session = Depends(get_db)):
    """Get all uploaded documents."""
    documents = db.query(Document).order_by(Document.uploaded_at.desc()).all()
    return documents

@app.post("/search-keyword")
async def search_keyword(request: KeywordSearchRequest, db: Session = Depends(get_db)):
    """Search for a keyword in the current document and return highlighted results."""
    global CURRENT_DOCUMENT
    
    if not CURRENT_DOCUMENT:
        raise HTTPException(status_code=400, detail="No document uploaded. Please upload a document first.")
    
    # Search for keyword
    search_result = search_keyword_in_document(CURRENT_DOCUMENT.filepath, request.keyword)
    
    # Format response for better display
    formatted_response = format_keyword_search_response(search_result, request.keyword)
    
    # Save search to database
    keyword_search = KeywordSearch(
        document_id=CURRENT_DOCUMENT.id,
        keyword=request.keyword,
        occurrences=search_result["occurrences"],
        locations=json.dumps(search_result["locations"])
    )
    db.add(keyword_search)
    db.commit()
    
    return {
        **search_result,
        "formatted_response": formatted_response
    }

def format_keyword_search_response(search_result: dict, keyword: str) -> str:
    """Format keyword search results as a readable response."""
    if not search_result["found"]:
        return f"❌ The keyword '{keyword}' was not found in the document."
    
    occurrences = search_result["occurrences"]
    pages = search_result["pages"]
    locations = search_result["locations"]
    
    response = f"Found '{keyword}' {occurrences} time(s) in the document.\n\n"
    response += f"**Pages:** {', '.join(map(str, pages))}\n\n"
    response += f"**Locations with context:**\n\n"
    
    for i, location in enumerate(locations[:10], 1):  # Show first 10 occurrences
        response += f"**{i}. Page {location['page']}:**\n"
        response += f"   {location['markdown_context']}\n\n"
    
    if occurrences > 10:
        response += f"\n... and {occurrences - 10} more occurrence(s)."
    
    return response

@app.post("/search-keywords")
async def search_keywords(request: MultipleKeywordSearchRequest, db: Session = Depends(get_db)):
    """Search for multiple keywords in the current document."""
    global CURRENT_DOCUMENT
    
    if not CURRENT_DOCUMENT:
        raise HTTPException(status_code=400, detail="No document uploaded. Please upload a document first.")
    
    # Search for all keywords
    search_results = search_multiple_keywords(CURRENT_DOCUMENT.filepath, request.keywords)
    
    return search_results
