from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
import os
import bcrypt
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

# Check if using Supabase
USE_SUPABASE = bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"))

if USE_SUPABASE:
    # Using Supabase - no direct database connection needed
    # All operations go through Supabase client
    print("Using Supabase for database operations")
    engine = None
    SessionLocal = None
else:
    # SQLite fallback for local development
    DATABASE_URL = "sqlite:///./chat_with_files.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print("Using SQLite database (local development)")

# Base class for models
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chat_histories = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password):
        """Hash and set password."""
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password):
        """Check if password matches."""
        try:
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            hash_bytes = self.password_hash.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except Exception:
            return False

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    mode = Column(String(20), default="rag")  # rag, generation, or search
    pdf_generated = Column(Boolean, default=False)
    pdf_url = Column(String(255), nullable=True)
    citations = Column(Text, nullable=True)  # JSON string of citations
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="chat_histories")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)  # For Supabase: stores storage path, for SQLite: local path
    file_type = Column(String(10), nullable=False)  # pdf, txt, docx
    file_size = Column(Integer, nullable=True)  # File size in bytes
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    supabase_path = Column(String(500), nullable=True)  # Supabase Storage path (bucket/path)
    
    # Relationship
    user = relationship("User", back_populates="documents")

class KeywordSearch(Base):
    __tablename__ = "keyword_searches"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=True)
    keyword = Column(String(255), nullable=False)
    occurrences = Column(Integer, default=0)
    locations = Column(Text, nullable=True)  # JSON string of page numbers/positions
    searched_at = Column(DateTime, default=datetime.utcnow)

# Create all tables
def init_db():
    """Initialize database and create all tables."""
    if USE_SUPABASE:
        # Supabase tables should be created via SQL editor or migrations
        # Just verify connection
        try:
            from .supabase_client import get_supabase_client
            supabase = get_supabase_client()
            # Test connection by querying a table
            supabase.table("users").select("id").limit(1).execute()
            print("Supabase connection verified!")
        except Exception as e:
            print(f"Supabase connection check: {e}")
            print("Note: Make sure tables are created in Supabase SQL Editor")
    else:
        # SQLite - create tables using SQLAlchemy
        Base.metadata.create_all(bind=engine)
    
    # Run migrations for existing databases (SQLite only)
    if not USE_SUPABASE:
        try:
            import sqlite3
            db_path = "./chat_with_files.db"
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Migration 1: Add citations column to chat_history if it doesn't exist
            cursor.execute("PRAGMA table_info(chat_history)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'citations' not in columns:
                print("Adding citations column to chat_history table...")
                cursor.execute("ALTER TABLE chat_history ADD COLUMN citations TEXT")
                conn.commit()
                print("Citations column added successfully!")
            
            # Migration 2: Add user_id column to chat_history if it doesn't exist
            if 'user_id' not in columns:
                print("Adding user_id column to chat_history table...")
                # First, check if there are existing records
                cursor.execute("SELECT COUNT(*) FROM chat_history")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    # If there are existing records, we need to assign them to a default user
                    # First, ensure users table exists and has at least one user
                    cursor.execute("SELECT COUNT(*) FROM users")
                    user_count = cursor.fetchone()[0]
                    
                    if user_count == 0:
                        # Create a default admin user for existing data
                        cursor.execute("""
                            INSERT INTO users (username, email, password_hash, created_at)
                            VALUES ('admin', 'admin@example.com', ?, datetime('now'))
                        """, ('$2b$12$default',))  # Placeholder hash
                        conn.commit()
                        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
                        default_user_id = cursor.fetchone()[0]
                    else:
                        cursor.execute("SELECT id FROM users LIMIT 1")
                        default_user_id = cursor.fetchone()[0]
                    
                    # Add user_id column with default value
                    cursor.execute("ALTER TABLE chat_history ADD COLUMN user_id INTEGER")
                    cursor.execute(f"UPDATE chat_history SET user_id = {default_user_id} WHERE user_id IS NULL")
                    cursor.execute("CREATE INDEX IF NOT EXISTS ix_chat_history_user_id ON chat_history(user_id)")
                else:
                    # No existing records, just add the column
                    cursor.execute("ALTER TABLE chat_history ADD COLUMN user_id INTEGER")
                    cursor.execute("CREATE INDEX IF NOT EXISTS ix_chat_history_user_id ON chat_history(user_id)")
                
                conn.commit()
                print("user_id column added to chat_history table!")
            
            # Migration 3: Add user_id column to documents if it doesn't exist
            cursor.execute("PRAGMA table_info(documents)")
            doc_columns = [row[1] for row in cursor.fetchall()]
            
            if 'user_id' not in doc_columns:
                print("Adding user_id column to documents table...")
                # Check if there are existing records
                cursor.execute("SELECT COUNT(*) FROM documents")
                doc_count = cursor.fetchone()[0]
                
                if doc_count > 0:
                    # Get default user ID
                    cursor.execute("SELECT COUNT(*) FROM users")
                    user_count = cursor.fetchone()[0]
                    
                    if user_count == 0:
                        cursor.execute("""
                            INSERT INTO users (username, email, password_hash, created_at)
                            VALUES ('admin', 'admin@example.com', ?, datetime('now'))
                        """, ('$2b$12$default',))
                        conn.commit()
                        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
                        default_user_id = cursor.fetchone()[0]
                    else:
                        cursor.execute("SELECT id FROM users LIMIT 1")
                        default_user_id = cursor.fetchone()[0]
                    
                    # Add user_id column with default value
                    cursor.execute("ALTER TABLE documents ADD COLUMN user_id INTEGER")
                    cursor.execute(f"UPDATE documents SET user_id = {default_user_id} WHERE user_id IS NULL")
                    cursor.execute("CREATE INDEX IF NOT EXISTS ix_documents_user_id ON documents(user_id)")
                else:
                    # No existing records, just add the column
                    cursor.execute("ALTER TABLE documents ADD COLUMN user_id INTEGER")
                    cursor.execute("CREATE INDEX IF NOT EXISTS ix_documents_user_id ON documents(user_id)")
                
                conn.commit()
                print("user_id column added to documents table!")
            
            # Migration 4: Add file_size column to documents if it doesn't exist
            if 'file_size' not in doc_columns:
                print("Adding file_size column to documents table...")
                cursor.execute("ALTER TABLE documents ADD COLUMN file_size INTEGER")
                # Set default value for existing records
                cursor.execute("UPDATE documents SET file_size = 0 WHERE file_size IS NULL")
                conn.commit()
                print("file_size column added to documents table!")
                
                conn.close()
        except Exception as e:
            print(f"Migration note: {e}")
    
    print("Database initialized successfully!")

# Dependency to get database session (for backward compatibility)
def get_db():
    """Get database session - returns None if using Supabase."""
    if USE_SUPABASE:
        # Return None - use Supabase client directly instead
        yield None
    else:
        # SQLite session
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
