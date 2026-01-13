# Render Deployment Fix - requirements.txt Error

## Problem
```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
```

## Solution Options

### Option 1: Set Root Directory in Render (Recommended)

If your repository structure is:
```
chat_files-backend-/
├── backend/
│   ├── requirements.txt
│   ├── app/
│   └── ...
```

**Fix:**
1. Render Dashboard la your service ku ponga
2. "Settings" tab click pannunga
3. "Root Directory" field la `backend` type pannunga
4. "Save Changes" click pannunga
5. Manual deploy trigger pannunga

### Option 2: Move requirements.txt to Repository Root

If your repository root is the backend folder:
```
chat_files-backend-/
├── requirements.txt  ← Ippol root la irukkanum
├── app/
└── ...
```

**Fix:**
1. GitHub repository la `requirements.txt` root folder la irukka check pannunga
2. Illana, `backend/requirements.txt` copy pannitu root la paste pannunga
3. Commit and push pannunga
4. Render auto-deploy pannum

### Option 3: Update Build Command

If Root Directory set pannala, build command la path specify pannunga:

**In Render Settings:**
- Build Command: `cd backend && pip install -r requirements.txt`
- Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Quick Fix Steps

### Step 1: Check Repository Structure
GitHub repository la check pannunga:
- `requirements.txt` enga irukku?
- Root la irukka? Or `backend/` folder la irukka?

### Step 2: Update Render Settings

**If `requirements.txt` is in `backend/` folder:**
1. Render Dashboard → Your Service → Settings
2. Root Directory: `backend` (type pannunga)
3. Save Changes
4. Manual Deploy

**If `requirements.txt` is in root:**
1. Root Directory: (empty or `.`)
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 3: Verify Files in Repository

Make sure these files are in the correct location:

**If Root Directory = `backend`:**
```
backend/
├── requirements.txt ✅
├── Procfile ✅
├── render.yaml ✅
├── app/
│   └── main.py ✅
└── ...
```

**If Root Directory = `.` (root):**
```
./
├── requirements.txt ✅
├── Procfile ✅
├── render.yaml ✅
├── app/
│   └── main.py ✅
└── ...
```

## Recommended Configuration

Based on your repository name `chat_files-backend-`, it seems like the repository root IS the backend folder.

**Recommended Settings:**
- **Root Directory**: `.` (empty or root)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## After Fix

1. Settings update pannumbodhu, "Manual Deploy" click pannunga
2. Logs check pannunga - build success aagum
3. If still error, repository structure verify pannunga

## Verify Repository Structure

GitHub la check pannunga:
```
https://github.com/k-indhumathi/chat_files-backend-
```

Files irukka check pannunga:
- ✅ `requirements.txt` - Root la irukkanum
- ✅ `app/main.py` - Root la irukkanum
- ✅ `Procfile` - Root la irukkanum (optional)

## Still Not Working?

1. Repository structure screenshot eduthu share pannunga
2. Render logs full error message check pannunga
3. Root Directory correct-a set pannirukka verify pannunga
