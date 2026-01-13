# How to Activate Virtual Environment

## ✅ Correct Commands for PowerShell

### Option 1: Activate.ps1 (Recommended)
```powershell
.\venv\Scripts\Activate.ps1
```

### Option 2: activate.bat
```powershell
.\venv\Scripts\activate
```

### Option 3: activate.bat (alternative)
```powershell
venv\Scripts\activate.bat
```

## ❌ Common Mistakes

### Wrong:
```powershell
\venv\scripts\activate    # Missing dot (.)
venv\scripts\activate    # Wrong case (scripts vs Scripts)
```

### Correct:
```powershell
.\venv\Scripts\Activate.ps1    # ✅ Correct!
```

## 📝 Notes

- Use `.\` (dot backslash) to run scripts in current directory
- Use `Scripts` (capital S) not `scripts`
- For PowerShell, prefer `Activate.ps1`
- After activation, you'll see `(venv)` in your prompt

## 🚀 Quick Start

```powershell
cd "C:\atman projects\chat-with-files\backend"
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```
