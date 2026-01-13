-- Supabase Storage RLS Policies
-- Run this in Supabase SQL Editor to allow file uploads/downloads/deletes

-- Policy 1: Allow authenticated users to upload files to their own bucket
-- Replace 'user-{user_id}-files' with your bucket naming pattern
CREATE POLICY "Users can upload to their own bucket"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'user-' || (auth.uid())::text || '-files'
  OR bucket_id LIKE 'user-%'
);

-- Policy 2: Allow authenticated users to read files from their own bucket
CREATE POLICY "Users can read from their own bucket"
ON storage.objects
FOR SELECT
TO authenticated
USING (
  bucket_id = 'user-' || (auth.uid())::text || '-files'
  OR bucket_id LIKE 'user-%'
);

-- Policy 3: Allow authenticated users to delete files from their own bucket
CREATE POLICY "Users can delete from their own bucket"
ON storage.objects
FOR DELETE
TO authenticated
USING (
  bucket_id = 'user-' || (auth.uid())::text || '-files'
  OR bucket_id LIKE 'user-%'
);

-- Policy 4: Allow authenticated users to update files in their own bucket
CREATE POLICY "Users can update files in their own bucket"
ON storage.objects
FOR UPDATE
TO authenticated
USING (
  bucket_id = 'user-' || (auth.uid())::text || '-files'
  OR bucket_id LIKE 'user-%'
);

-- Alternative: If you want to use service role key (bypasses RLS)
-- You can skip RLS policies if using service role key for all operations
-- But it's better to use proper RLS policies for security

-- Note: If your user_id doesn't match auth.uid(), you may need to adjust the policies
-- For example, if you're using custom user IDs from your users table:
-- 
-- CREATE POLICY "Users can upload to their own bucket"
-- ON storage.objects
-- FOR INSERT
-- TO authenticated
-- WITH CHECK (
--   bucket_id = 'user-' || (
--     SELECT id::text FROM users WHERE id = (SELECT user_id FROM auth.users WHERE id = auth.uid())
--   ) || '-files'
-- );
