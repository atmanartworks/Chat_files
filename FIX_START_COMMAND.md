# Fix: Could not import module "main"

## Problem
```
ERROR: Error loading ASGI app. Could not import module "main".
Running 'uvicorn main:app --host 0.0.0.0 --port $PORT'
```

## Solution

Render Dashboard la Start Command wrong-a set pannirukku. Fix pannunga:

### Step 1: Render Dashboard Settings
1. Render Dashboard la your service (`chat_files-backend-`) click pannunga
2. "Settings" tab click pannunga
3. Scroll down to "Start Command" section

### Step 2: Update Start Command
**Current (Wrong):**
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Correct:**
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Step 3: Save and Deploy
1. "Save Changes" click pannunga
2. "Manual Deploy" click pannunga
3. Wait for deployment

## Why This Error?

Your project structure:
```
backend/
├── app/
│   └── main.py  ← main.py is inside app/ folder
└── requirements.txt
```

So the correct import path is `app.main:app`, not `main:app`.

## Alternative: If Root Directory is Set

If Root Directory = `backend`:
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` ✅

If Root Directory = `.` (root):
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` ✅
- (Same command, because app/ folder is relative to root)

## Quick Fix Checklist

- [ ] Render Dashboard → Settings
- [ ] Start Command field la: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Save Changes
- [ ] Manual Deploy
- [ ] Check logs - should work now!

## Verify

After fix, logs la intha line varum:
```
Running 'uvicorn app.main:app --host 0.0.0.0 --port $PORT'
```

And error illama application start aagum! ✅
