# 🚀 Deploy Backend to Render - Step by Step Guide

## ✅ Your Project is Ready!

Your backend is already configured with:
- ✅ `Procfile` - Correct start command
- ✅ `requirements.txt` - All dependencies listed
- ✅ `render.yaml` - Configuration file (optional, but helpful)
- ✅ Code pushed to GitHub: https://github.com/atmanartworks/Chat_files

## 📋 Step-by-Step Instructions

### Step 1: Open Render Dashboard
1. Go to: https://dashboard.render.com/web/new?onboarding=active
2. Sign in with your GitHub account (if not already signed in)

### Step 2: Create New Web Service
1. Click the **"New +"** button (top right)
2. Select **"Web Service"**

### Step 3: Connect Your Repository
1. Under **"Connect a repository"**, you'll see:
   - If GitHub is connected: Select **"atmanartworks/Chat_files"** from the list
   - If not connected: Click **"Connect account"** → Authorize → Then select your repo

### Step 4: Configure Service Settings

Fill in these **EXACT** values:

#### Basic Settings:
- **Name**: `foundergpt-backend` (or any name you prefer)
- **Region**: Choose closest to you (Singapore, US East, or EU West)
- **Branch**: `main`
- **Root Directory**: `backend` ⚠️ **IMPORTANT: Enter "backend" here**

#### Build & Deploy:
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### Plan:
- **Free** (for testing) or **Starter** ($7/month for always-on)

### Step 5: Add Environment Variables

Click **"Add Environment Variable"** for each of these:

#### Required Variables:

```
SUPABASE_URL = (Your Supabase project URL)
SUPABASE_KEY = (Your Supabase anon key)
SUPABASE_SERVICE_KEY = (Your Supabase service role key)
QDRANT_URL = (Your Qdrant Cloud URL)
QDRANT_API_KEY = (Your Qdrant API key)
GROQ_API_KEY = (Your Groq API key)
SECRET_KEY = (Click "Generate" button in Render, or use a random string)
```

#### Optional Variables:

```
PYTHON_VERSION = 3.11.0
DATABASE_URL = (Your Supabase PostgreSQL connection string, if needed)
```

**Where to find these values:**
- **Supabase**: Dashboard → Settings → API
- **Qdrant**: Qdrant Cloud Dashboard → Your Cluster → API Key
- **Groq**: https://console.groq.com → API Keys
- **SECRET_KEY**: Click "Generate" in Render dashboard (or use any random string)

### Step 6: Deploy!

1. Scroll down and click **"Create Web Service"**
2. Render will start building (takes 5-10 minutes)
3. Watch the logs - you'll see:
   - Installing dependencies...
   - Building application...
   - Starting service...
   - ✅ "FounderGPT API Ready"

### Step 7: Verify Deployment

Once deployed, you'll get a URL like: `https://foundergpt-backend.onrender.com`

Test it:
1. Open: `https://your-app-name.onrender.com/`
2. Should see: `{"status":"ok","message":"FounderGPT API is running","service":"backend"}`
3. Open: `https://your-app-name.onrender.com/docs` (API documentation)

## ⚠️ Important Notes

1. **Root Directory**: Must be `backend` (not empty, not `.`)
2. **Start Command**: Must use `$PORT` (Render sets this automatically)
3. **Environment Variables**: All must be set before deployment
4. **Free Tier**: Service sleeps after 15 min inactivity (takes 30-60 sec to wake up)

## 🐛 Troubleshooting

### Build Fails?
- Check Root Directory is set to `backend`
- Verify `requirements.txt` exists in backend folder
- Check logs for specific error

### Service Won't Start?
- Verify Start Command is exactly: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Check all environment variables are set
- Look at logs for error messages

### Can't Connect?
- Wait 1-2 minutes after deployment
- Check service status is "Live" (green)
- Verify URL is correct

## 📝 After Deployment

1. **Save your Render URL** - You'll need it for frontend
2. **Update CORS** (if deploying frontend later):
   - Edit `backend/app/main.py`
   - Add your frontend URL to `allow_origins` list
   - Commit and push (auto-deploys)

## 🎉 You're Done!

Your backend is now live! The URL will be shown in the Render dashboard.

**Next Steps:**
- Test the API endpoints
- Update frontend to use the new backend URL
- Deploy frontend (if needed)

---

**Need Help?** Check the logs in Render dashboard → Your Service → Logs tab
