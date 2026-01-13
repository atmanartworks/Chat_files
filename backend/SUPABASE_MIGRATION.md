# Supabase Migration Guide

This guide will help you migrate your chat-with-files project from SQLite to Supabase.

## Prerequisites

1. **Supabase Account**: Sign up at https://supabase.com
2. **Supabase Project**: Create a new project in Supabase dashboard

## Step 1: Get Supabase Credentials

1. Go to your Supabase project dashboard
2. Click on **Settings** → **API**
3. Copy the following:
   - **Project URL** (SUPABASE_URL)
   - **anon/public key** (SUPABASE_KEY)
   - **Database URL** (DATABASE_URL) - from Settings → Database → Connection string

## Step 2: Update Environment Variables

Add these to your `backend/.env` file:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.your-project-id.supabase.co:5432/postgres

# Keep existing variables
GROQ_API_KEY=your-groq-key
QDRANT_URL=your-qdrant-url
QDRANT_API_KEY=your-qdrant-key
SECRET_KEY=your-secret-key
```

## Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install:
- `psycopg2-binary` (PostgreSQL driver)
- `supabase` (Supabase Python client)

## Step 4: Run Database Migration

The database schema will be automatically created when you start the server. However, if you need to migrate existing data:

```bash
python migrate_to_supabase.py
```

This script will:
- Copy all users from SQLite to Supabase
- Copy all documents and upload files to Supabase Storage
- Copy all chat history
- Copy all keyword searches

## Step 5: Set Up Supabase Storage Buckets

The application will automatically create storage buckets for each user. However, you can also create them manually:

1. Go to **Storage** in Supabase dashboard
2. Create buckets named: `user-1-files`, `user-2-files`, etc. (or let the app create them automatically)
3. Set bucket policies to allow authenticated users to read/write their own files

## Step 6: Update Database Schema (if needed)

If you're starting fresh, the schema will be created automatically. If you need to add the `supabase_path` column:

```sql
ALTER TABLE documents ADD COLUMN supabase_path VARCHAR(500);
```

## Step 7: Test the Migration

1. Restart your server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Test file upload:
   - Upload a file through the UI
   - Check Supabase Storage to verify the file was uploaded

3. Test file download:
   - Try to access a file
   - Verify it downloads correctly

## Features

### Automatic Fallback
- If Supabase credentials are not set, the app will fall back to local SQLite storage
- This allows for gradual migration or local development

### File Storage
- Files are stored in Supabase Storage (cloud)
- Each user has their own bucket: `user-{user_id}-files`
- Files are automatically uploaded when users upload documents

### Database
- PostgreSQL database hosted on Supabase
- All tables are automatically created
- Relationships and indexes are preserved

## Troubleshooting

### Connection Issues
- Verify your DATABASE_URL is correct
- Check that your Supabase project is active
- Ensure your IP is allowed (Supabase allows all IPs by default)

### Storage Issues
- Verify SUPABASE_URL and SUPABASE_KEY are correct
- Check bucket policies in Supabase dashboard
- Ensure buckets are created (they're created automatically on first upload)

### Migration Issues
- If migration fails, check the error messages
- Some data might need manual migration
- Always backup your SQLite database before migration

## Benefits of Supabase

1. **Scalability**: PostgreSQL can handle much larger datasets
2. **Cloud Storage**: Files are stored in the cloud, accessible from anywhere
3. **Backup**: Automatic backups in Supabase
4. **Performance**: Better performance for concurrent users
5. **Security**: Built-in authentication and row-level security

## Rollback

If you need to rollback to SQLite:
1. Remove SUPABASE_URL and SUPABASE_KEY from .env
2. Set DATABASE_URL back to `sqlite:///./chat_with_files.db`
3. Restart the server

The app will automatically use SQLite if Supabase credentials are not available.
