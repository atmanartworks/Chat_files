# 🚀 Render Quick Start - FounderGPT Backend

## ⚡ 5-Minute Deployment

### 1. Push Code
```bash
git add .
git commit -m "Ready for Render"
git push
```

### 2. Create Service on Render
1. Go to https://render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository

### 3. Configure
- **Name**: `foundergpt-backend`
- **Root Directory**: `.` (or `backend` if in subfolder)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 4. Add Environment Variables
```
SUPABASE_URL = your-url
SUPABASE_KEY = your-key
SUPABASE_SERVICE_KEY = your-service-key
QDRANT_URL = your-url
QDRANT_API_KEY = your-key
GROQ_API_KEY = your-key
SECRET_KEY = (generate)
```

### 5. Deploy!
Click **"Create Web Service"** and wait 5-10 minutes.

## ✅ Verify
- Visit: `https://your-app.onrender.com/health`
- Should return: `{"status": "ok"}`

## 📚 Full Guide
See `DEPLOY_TO_RENDER.md` for complete instructions.
