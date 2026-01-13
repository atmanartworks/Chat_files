# Test Authentication Endpoints

## Check if Users Table Exists in Supabase

1. Go to Supabase Dashboard → **Table Editor**
2. Check if `users` table exists
3. If not, run this SQL in **SQL Editor**:

```sql
-- Create users table if it doesn't exist
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
```

## Test Register Endpoint

```bash
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@test.com","password":"test123"}'
```

## Test Login Endpoint

```bash
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=test123"
```

## Common Issues

1. **Users table doesn't exist** - Create it using SQL above
2. **RLS policies blocking** - Disable RLS or add policies for users table
3. **Connection error** - Check SUPABASE_URL and SUPABASE_KEY in .env
