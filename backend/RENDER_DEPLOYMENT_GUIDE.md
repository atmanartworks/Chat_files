# 🚀 Render Deployment Guide - FounderGPT Backend

## ✅ Pre-Deployment Checklist

### 1. Code Ready
- [x] All code committed to Git
- [x] `requirements.txt` updated
- [x] `render.yaml` configured
- [x] `Procfile` created
- [x] `.gitignore` configured
- [x] Error handling in place
- [x] Health check endpoints added

### 2. Environment Variables Ready
Prepare these values before deployment:
- [ ] `SUPABASE_URL` - Your Supabase project URL
- [ ] `SUPABASE_KEY` - Your Supabase anon key
- [ ] `SUPABASE_SERVICE_KEY` - Your Supabase service role key
- [ ] `QDRANT_URL` - Your Qdrant Cloud URL
- [ ] `QDRANT_API_KEY` - Your Qdrant API key
- [ ] `GROQ_API_KEY` - Your Groq API key
- [ ] `SECRET_KEY` - JWT secret (Render can auto-generate)
- [ ] `DATABASE_URL` - Supabase PostgreSQL connection string (optional)

## 📋 Step-by-Step Deployment

### Step 1: Push Code to GitHub

```bash
# Navigate to project root
cd "C:\atman projects\chat-with-files"

# Check status
git status

# Add all files
git add .

# Commit
git commit -m "Ready for Render deployment"

# Push to GitHub
git push origin main
```

### Step 2: Create Render Account

1. Go to https://render.com
2. Click "Get Started" or "Sign Up"
3. Sign up with GitHub (recommended)
4. Authorize Render to access your repositories

### Step 3: Create New Web Service

1. In Render Dashboard, click **"New +"** button
2. Select **"Web Service"**
3. Connect your repository:
   - Click **"Connect account"** if not connected
   - Select your GitHub account
   - Find and select your repository: `chat_files-backend-` (or your repo name)
   - Click **"Connect"**

### Step 4: Configure Service

Fill in the following settings:

#### Basic Settings:
- **Name**: `foundergpt-backend` (or your preferred name)
- **Region**: Choose closest to your users
  - **Singapore** (for Asia)
  - **US East** (for US)
  - **EU West** (for Europe)
- **Branch**: `main` (or `master`)
- **Root Directory**: 
  - If repository root IS backend folder: Leave **empty** or `.`
  - If backend is in subfolder: Enter `backend`

#### Build & Deploy:
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### Advanced Settings:
- **Instance Type**: `Free` (for testing) or `Starter` (for production)
- **Auto-Deploy**: `Yes` (deploys on every push)

### Step 5: Set Environment Variables

1. Scroll down to **"Environment Variables"** section
2. Click **"Add Environment Variable"** for each:

#### Required Variables:

```
SUPABASE_URL = https://your-project.supabase.co
SUPABASE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
QDRANT_URL = https://your-cluster.qdrant.io
QDRANT_API_KEY = your-qdrant-api-key
GROQ_API_KEY = gsk_your-groq-api-key
SECRET_KEY = (Click "Generate" or use a random string)
```

#### Optional Variables:

```
DATABASE_URL = postgresql://user:pass@host:port/dbname
PYTHON_VERSION = 3.11.0
```

**Important:**
- Never commit `.env` file to Git
- All sensitive keys must be in Render dashboard
- Use "Generate" button for `SECRET_KEY` if unsure

### Step 6: Deploy

1. Review all settings
2. Click **"Create Web Service"**
3. Render will start building:
   - Installing dependencies (5-10 minutes)
   - Building application
   - Starting service
4. Watch the logs for progress

### Step 7: Monitor Deployment

1. **Build Phase:**
   - Watch for: `Installing dependencies...`
   - Should see: `Successfully installed...`
   - Should see: `Build successful ✅`

2. **Deploy Phase:**
   - Watch for: `Deploying...`
   - Should see: `FounderGPT API Starting...`
   - Should see: `FounderGPT API Ready - Port binding should succeed now`
   - Should see: `INFO: Uvicorn running on http://0.0.0.0:XXXX`

3. **Success Indicators:**
   - ✅ Green "Live" status
   - ✅ Service URL displayed
   - ✅ No error messages in logs

### Step 8: Verify Deployment

#### Test Root Endpoint:
```bash
curl https://your-app.onrender.com/
```

Expected Response:
```json
{
  "status": "ok",
  "message": "FounderGPT API is running",
  "service": "backend"
}
```

#### Test Health Endpoint:
```bash
curl https://your-app.onrender.com/health
```

#### Test API Docs:
Open in browser:
```
https://your-app.onrender.com/docs
```

Should show FastAPI interactive documentation.

## 🔧 Post-Deployment Configuration

### Update CORS for Production

After deployment, update `backend/app/main.py` CORS settings:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-domain.com",  # Add your frontend URL
        "http://localhost:5173",  # Keep for local dev
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then commit and push:
```bash
git add backend/app/main.py
git commit -m "Update CORS for production"
git push
```

### Update Frontend API URL

In `frontend/src/services/api.js`, update base URL:

```javascript
const API_BASE_URL = 'https://your-app.onrender.com';
```

## 🐛 Troubleshooting

### Build Fails

**Error**: `ERROR: Could not open requirements file`
- **Fix**: Check Root Directory setting
- If backend is in subfolder: Set Root Directory to `backend`
- If repo root is backend: Leave empty

**Error**: `ModuleNotFoundError`
- **Fix**: Check `requirements.txt` has all dependencies
- Verify Python version (3.11.0 recommended)

### Deployment Fails

**Error**: `No open ports detected`
- **Fix**: Check Start Command is correct
- Should be: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Check logs for startup errors

**Error**: `Could not import module "main"`
- **Fix**: Check Start Command
- Should be: `uvicorn app.main:app` (not `uvicorn main:app`)

### Service Crashes

**Error**: Database connection failed
- **Fix**: Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Check Supabase project is active

**Error**: Qdrant connection failed
- **Fix**: Verify `QDRANT_URL` and `QDRANT_API_KEY` are correct
- Check Qdrant cluster is active

**Error**: Application startup timeout
- **Fix**: Check logs for specific errors
- Verify all environment variables are set
- Check startup code for blocking operations

## 📊 Monitoring

### View Logs:
1. Render Dashboard → Your Service
2. Click **"Logs"** tab
3. View real-time logs
4. Filter by time range

### Check Metrics:
1. Render Dashboard → Your Service
2. Click **"Metrics"** tab
3. View CPU, Memory, Request metrics

### Set Up Alerts:
1. Render Dashboard → Your Service
2. Click **"Alerts"** tab
3. Configure email/Slack notifications

## 🔄 Updating Deployment

### Automatic Updates:
- Render auto-deploys on every `git push`
- No manual action needed

### Manual Deploy:
1. Render Dashboard → Your Service
2. Click **"Manual Deploy"**
3. Select branch/commit
4. Click **"Deploy"**

### Rollback:
1. Render Dashboard → Your Service
2. Click **"Events"** tab
3. Find previous successful deployment
4. Click **"Rollback"**

## 💰 Free Tier Limitations

- **Sleep After**: 15 minutes of inactivity
- **Cold Start**: 30-60 seconds after sleep
- **Build Time**: Limited to 10 minutes
- **Bandwidth**: 100 GB/month

**Upgrade to Paid:**
- Always-on service
- Faster cold starts
- More resources
- Better performance

## ✅ Success Checklist

After deployment, verify:
- [ ] Service shows "Live" status
- [ ] Root endpoint returns 200 OK
- [ ] Health endpoint returns 200 OK
- [ ] API docs accessible
- [ ] No errors in logs
- [ ] Can register/login
- [ ] Can upload files
- [ ] Can chat with documents

## 📞 Support

- **Render Docs**: https://render.com/docs
- **Render Status**: https://status.render.com
- **Render Community**: https://community.render.com

## 🎉 You're Done!

Your FounderGPT backend is now live on Render! 🚀

**Your API URL**: `https://your-app.onrender.com`

Update your frontend to use this URL and you're ready to go!
