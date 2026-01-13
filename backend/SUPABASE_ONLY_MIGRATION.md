# Supabase-Only Migration Guide

Your project has been migrated to use **only Supabase client** (no direct PostgreSQL connection).

## What Changed

### 1. Database Operations
- **Before**: Direct PostgreSQL connection via SQLAlchemy
- **After**: Supabase client using PostgREST API
- **Fallback**: SQLite for local development (if Supabase credentials not set)

### 2. File Storage
- **Before**: Local file system
- **After**: Supabase Storage (cloud)
- **Fallback**: Local storage if Supabase credentials not set

### 3. New Files Created
- `backend/app/supabase_client.py` - Supabase client configuration
- `backend/app/supabase_db.py` - Database operations using Supabase
- `backend/app/supabase_storage.py` - File storage operations
- `backend/app/file_loader_helper.py` - Unified file loading
- `backend/app/db_helper.py` - Unified database helper

## Setup Instructions

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Get Supabase Credentials
1. Go to https://supabase.com
2. Create account and project
3. Go to **Settings** → **API**
4. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon/public key** → `SUPABASE_KEY`

### 3. Update `.env` File
```env
# Supabase Configuration (REQUIRED for Supabase mode)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here

# Remove DATABASE_URL - not needed anymore!
# DATABASE_URL is NOT used - Supabase client handles it internally

# Keep existing
GROQ_API_KEY=your-groq-key
QDRANT_URL=your-qdrant-url
QDRANT_API_KEY=your-qdrant-key
SECRET_KEY=your-secret-key
```

### 4. Create Tables in Supabase
Go to Supabase Dashboard → **SQL Editor** and run:

```sql
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    filepath VARCHAR(500) NOT NULL,
    file_type VARCHAR(10) NOT NULL,
    file_size INTEGER,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    supabase_path VARCHAR(500)
);

-- Chat history table
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    mode VARCHAR(20) DEFAULT 'rag',
    pdf_generated BOOLEAN DEFAULT FALSE,
    pdf_url VARCHAR(255),
    citations TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Keyword searches table
CREATE TABLE IF NOT EXISTS keyword_searches (
    id SERIAL PRIMARY KEY,
    document_id INTEGER,
    keyword VARCHAR(255) NOT NULL,
    occurrences INTEGER DEFAULT 0,
    locations TEXT,
    searched_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);
```

### 5. Set Up Storage Buckets
Storage buckets are created automatically on first upload. Or create manually:

1. Go to **Storage** in Supabase dashboard
2. Create buckets: `user-1-files`, `user-2-files`, etc. (or let app create them)
3. Set policies to allow authenticated users to read/write their own files

### 6. Run Migration Script (Optional)
If you have existing SQLite data:

```bash
python migrate_to_supabase.py
```

### 7. Restart Server
```bash
uvicorn app.main:app --reload
```

## How It Works

### Automatic Detection
- If `SUPABASE_URL` and `SUPABASE_KEY` are set → Uses Supabase
- If not set → Falls back to SQLite (local development)

### Database Operations
All database operations go through Supabase client:
- `supabase.table("users").select()` - Read
- `supabase.table("users").insert()` - Create
- `supabase.table("users").update()` - Update
- `supabase.table("users").delete()` - Delete

### File Storage
- Files uploaded → Supabase Storage
- Files downloaded → From Supabase Storage when needed
- Files deleted → From Supabase Storage

## Benefits

1. **No Direct PostgreSQL Connection**: Uses Supabase's managed API
2. **Automatic Scaling**: Supabase handles scaling
3. **Built-in Security**: Row-level security, authentication
4. **Cloud Storage**: Files stored in cloud, accessible anywhere
5. **Backup**: Automatic backups in Supabase
6. **Monitoring**: Built-in dashboard and monitoring

## Troubleshooting

### "SUPABASE_URL and SUPABASE_KEY must be set"
- Add credentials to `.env` file
- Restart server

### "Table does not exist"
- Run SQL script in Supabase SQL Editor
- Or let app create tables automatically (if permissions allow)

### "Storage bucket not found"
- Buckets are created automatically on first upload
- Or create manually in Supabase dashboard

### Files not uploading
- Check Supabase Storage policies
- Ensure bucket exists
- Check API key permissions

## Migration Complete!

Your project now uses **only Supabase client** - no direct PostgreSQL connections. All database and storage operations go through Supabase's managed API.
