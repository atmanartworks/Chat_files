# 🚀 Deploy FounderGPT Backend to Render - Complete Guide

## ✅ Pre-Deployment Checklist

Before deploying, ensure:

- [x] Code is committed to Git
- [x] GitHub repository is ready
- [x] All environment variables are noted
- [x] `requirements.txt` is up to date
- [x] `render.yaml` is configured
- [x] `Procfile` exists

## 📋 Step-by-Step Deployment

### Step 1: Prepare Your Code

```bash
# Navigate to project
cd "C:\atman projects\chat-with-files"

# Check Git status
git status

# Add all files
git add .

# Commit
git commit -m "Ready for Render deployment - FounderGPT Backend"

# Push to GitHub
git push origin main
```

### Step 2: Create Render Account

1. Go to **https://render.com**
2. Click **"Get Started"** or **"Sign Up"**
3. Choose **"Sign up with GitHub"** (recommended)
4. Authorize Render to access your repositories

### Step 3: Create New Web Service

1. In Render Dashboard, click **"New +"** button (top right)
2. Select **"Web Service"**
3. **Connect Repository:**
   - If not connected, click **"Connect account"**
   - Select your GitHub account
   - Find your repository: `chat_files-backend-` (or your repo name)
   - Click **"Connect"**

### Step 4: Configure Service Settings

#### Basic Configuration:

| Setting | Value |
|---------|-------|
| **Name** | `foundergpt-backend` |
| **Region** | Singapore / US East / EU West (choose closest) |
| **Branch** | `main` |
| **Root Directory** | `.` (if repo root is backend) OR `backend` (if backend is subfolder) |

#### Build & Start:

| Setting | Value |
|---------|-------|
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

#### Instance Type:
- **Free** (for testing) - Sleeps after 15 min inactivity
- **Starter** ($7/month) - Always on, better performance

### Step 5: Set Environment Variables

Click **"Advanced"** → **"Environment Variables"** → **"Add Environment Variable"**

#### Required Variables:

```
SUPABASE_URL
Value: https://your-project-id.supabase.co

SUPABASE_KEY
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (anon key)

SUPABASE_SERVICE_KEY
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (service role key)

QDRANT_URL
Value: https://your-cluster-id.qdrant.io

QDRANT_API_KEY
Value: your-qdrant-api-key-here

GROQ_API_KEY
Value: gsk_your-groq-api-key-here

SECRET_KEY
Value: (Click "Generate" button or use random string)
```

#### Optional Variables:

```
DATABASE_URL
Value: postgresql://user:pass@host:port/dbname (if using Supabase PostgreSQL)

PYTHON_VERSION
Value: 3.11.0
```

**Important Notes:**
- ✅ Never commit `.env` file to Git
- ✅ All values must be set in Render dashboard
- ✅ Use "Generate" for SECRET_KEY if unsure
- ✅ Double-check all URLs and keys for typos

### Step 6: Deploy

1. Review all settings
2. Click **"Create Web Service"**
3. Render will start building:
   - **Build Phase** (5-10 minutes):
     - Installing Python dependencies
     - Building application
   - **Deploy Phase** (1-2 minutes):
     - Starting application
     - Binding to port

### Step 7: Monitor Deployment

Watch the **Logs** tab for:

#### ✅ Success Indicators:
```
==> Building...
==> Installing dependencies...
==> Successfully installed...
==> Build successful ✅
==> Deploying...
FounderGPT API Starting...
==================================================
Database connected and initialized!
Startup completed - application ready to accept requests
==================================================
FounderGPT API Ready - Port binding should succeed now
==================================================
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:XXXX
==> Your service is live 🎉
```

#### ❌ Error Indicators:
- `ERROR: Could not open requirements file` → Check Root Directory
- `No open ports detected` → Check Start Command
- `Could not import module` → Check Start Command path
- `Database connection failed` → Check environment variables

### Step 8: Verify Deployment

#### Test Endpoints:

1. **Root Endpoint:**
   ```bash
   curl https://your-app.onrender.com/
   ```
   Expected: `{"status": "ok", "message": "FounderGPT API is running"}`

2. **Health Check:**
   ```bash
   curl https://your-app.onrender.com/health
   ```

3. **API Documentation:**
   Open in browser: `https://your-app.onrender.com/docs`

## 🔧 Post-Deployment

### Update CORS for Frontend

After frontend is deployed, update CORS in `backend/app/main.py`:

```python
allow_origins=[
    "https://your-frontend-domain.com",  # Add your frontend URL
    "http://localhost:5173",
    # ... other origins
],
```

Then commit and push:
```bash
git add backend/app/main.py
git commit -m "Update CORS for production frontend"
git push
```

### Update Frontend API URL

In `frontend/src/services/api.js`:

```javascript
const API_BASE_URL = 'https://your-backend.onrender.com';
```

## 🐛 Common Issues & Fixes

### Issue 1: Build Fails - requirements.txt not found
**Error**: `ERROR: Could not open requirements file`

**Fix:**
- Check **Root Directory** setting
- If backend is in subfolder: Set to `backend`
- If repo root is backend: Leave empty or `.`

### Issue 2: Port Not Detected
**Error**: `No open ports detected`

**Fix:**
- Verify **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Check logs for startup errors
- Ensure app doesn't crash during startup

### Issue 3: Module Import Error
**Error**: `Could not import module "main"`

**Fix:**
- Check **Start Command** path
- Should be: `uvicorn app.main:app` (not `uvicorn main:app`)
- Verify Root Directory is correct

### Issue 4: Database Connection Failed
**Error**: `Database initialization error`

**Fix:**
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Check Supabase project is active
- Verify network connectivity

### Issue 5: Service Crashes
**Error**: Service shows "Crashed" status

**Fix:**
- Check **Logs** tab for error messages
- Verify all environment variables are set
- Check for missing dependencies
- Review startup code for errors

## 📊 Monitoring & Maintenance

### View Logs:
1. Render Dashboard → Your Service
2. Click **"Logs"** tab
3. View real-time or historical logs
4. Filter by time range

### Check Metrics:
1. Render Dashboard → Your Service
2. Click **"Metrics"** tab
3. View:
   - CPU usage
   - Memory usage
   - Request rate
   - Response times

### Set Up Alerts:
1. Render Dashboard → Your Service
2. Click **"Alerts"** tab
3. Configure notifications for:
   - Deployment failures
   - Service crashes
   - High resource usage

## 🔄 Updating Your Deployment

### Automatic Updates:
- Render auto-deploys on every `git push`
- No manual action needed
- Monitor logs for deployment status

### Manual Deploy:
1. Render Dashboard → Your Service
2. Click **"Manual Deploy"** button
3. Select branch/commit
4. Click **"Deploy"**

### Rollback:
1. Render Dashboard → Your Service
2. Click **"Events"** tab
3. Find previous successful deployment
4. Click **"Rollback"** button

## 💰 Pricing

### Free Tier:
- ✅ 750 hours/month
- ✅ Sleeps after 15 min inactivity
- ✅ 30-60 second cold start
- ✅ 100 GB bandwidth/month
- ✅ 512 MB RAM

### Starter Plan ($7/month):
- ✅ Always-on service
- ✅ Faster cold starts
- ✅ 512 MB RAM
- ✅ Better performance

## ✅ Final Checklist

After deployment, verify:

- [ ] Service shows **"Live"** status
- [ ] Root endpoint (`/`) returns 200 OK
- [ ] Health endpoint (`/health`) returns 200 OK
- [ ] API docs (`/docs`) accessible
- [ ] No errors in logs
- [ ] Can register new users
- [ ] Can login
- [ ] Can upload files
- [ ] Can chat with documents
- [ ] Citations working

## 🎉 Success!

Your FounderGPT backend is now live on Render! 🚀

**Your API URL**: `https://your-app.onrender.com`

**Next Steps:**
1. Update frontend API URL
2. Test all endpoints
3. Monitor logs for any issues
4. Set up alerts for production

## 📞 Support

- **Render Docs**: https://render.com/docs
- **Render Status**: https://status.render.com
- **Render Community**: https://community.render.com

---

**Need Help?** Check `RENDER_DEPLOYMENT_GUIDE.md` for detailed troubleshooting.
