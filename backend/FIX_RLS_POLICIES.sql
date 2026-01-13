-- Fix RLS Policies for Supabase Tables
-- Run this in Supabase SQL Editor to allow operations

-- 1. Disable RLS on users table (or add policies)
ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- OR if you want to keep RLS enabled, add policies:
-- Allow anyone to insert (for registration)
-- CREATE POLICY "Allow public registration" ON users FOR INSERT TO anon WITH CHECK (true);
-- Allow authenticated users to read their own data
-- CREATE POLICY "Users can read own data" ON users FOR SELECT TO authenticated USING (auth.uid() = id);

-- 2. Disable RLS on documents table
ALTER TABLE documents DISABLE ROW LEVEL SECURITY;

-- 3. Disable RLS on chat_history table
ALTER TABLE chat_history DISABLE ROW LEVEL SECURITY;

-- 4. Disable RLS on storage.objects (for file uploads)
-- Note: This is done via Supabase Dashboard → Storage → Policies
-- Or use service role key which bypasses RLS

-- Verify RLS status
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'documents', 'chat_history');
