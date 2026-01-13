# How to Run Frontend and Backend

## ✅ Database Status
**No database connection needed!** The app uses in-memory storage.

## 🚀 Quick Start

### Option 1: Run Both Servers (Recommended)

**Terminal 1 - Backend:**
```powershell
cd "C:\atman projects\chat-with-files\backend"
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```powershell
cd "C:\atman projects\chat-with-files\frontend"
npm run dev
```

### Option 2: Use Start Scripts

**Backend:**
```powershell
.\START_BACKEND.ps1
```

**Frontend:**
```powershell
.\START_FRONTEND.ps1
```

## 📍 URLs

- **Backend API:** http://127.0.0.1:8000
- **Backend Docs:** http://127.0.0.1:8000/docs
- **Frontend:** http://localhost:5173

## ✅ Verification

1. Backend running: Check http://127.0.0.1:8000/docs
2. Frontend running: Check http://localhost:5173
3. Both working: Upload a file and chat!
