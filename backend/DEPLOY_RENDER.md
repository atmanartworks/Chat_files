# Render Deployment Guide - Backend Only

## Step-by-Step Instructions

### Step 1: Prepare Your Code
1. Make sure all your code is committed to Git (GitHub/GitLab/Bitbucket)
2. Ensure `requirements.txt` is up to date
3. Make sure `render.yaml` is in the `backend` folder

### Step 2: Create Render Account
1. Go to https://render.com
2. Sign up or Log in
3. Click "New +" button

### Step 3: Create New Web Service
1. Click "New Web Service"
2. Connect your Git repository:
   - Select GitHub/GitLab/Bitbucket
   - Authorize Render to access your repository
   - Select your repository

### Step 4: Configure Service
1. **Name**: `foundergpt-backend` (or your preferred name)
2. **Region**: Choose closest to your users (e.g., Singapore, US East)
3. **Branch**: `main` or `master`
4. **Root Directory**: `backend` (important!)
5. **Runtime**: `Python 3`
6. **Build Command**: `pip install -r requirements.txt`
7. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 5: Set Environment Variables
Click "Advanced" and add these environment variables:

**Required:**
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key
- `SUPABASE_SERVICE_KEY` - Your Supabase service role key
- `QDRANT_URL` - Your Qdrant Cloud URL
- `QDRANT_API_KEY` - Your Qdrant API key
- `GROQ_API_KEY` - Your Groq API key
- `SECRET_KEY` - JWT secret (Render can generate this)
- `DATABASE_URL` - Your Supabase PostgreSQL connection string (if using)

**Optional:**
- `PYTHON_VERSION` - Set to `3.11.0` (or your preferred version)

### Step 6: Deploy
1. Click "Create Web Service"
2. Render will start building and deploying
3. Wait for deployment to complete (5-10 minutes)
4. Check logs for any errors

### Step 7: Update CORS Settings
After deployment, update your backend CORS in `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-domain.com",  # Add your frontend URL
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 8: Get Your Backend URL
1. After successful deployment, you'll get a URL like:
   `https://foundergpt-backend.onrender.com`
2. Update your frontend API base URL to this new URL

### Step 9: Test Your Deployment
1. Visit: `https://your-backend-url.onrender.com/docs` (FastAPI docs)
2. Test your endpoints
3. Check logs in Render dashboard

## Important Notes

### Free Tier Limitations:
- Services sleep after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds (cold start)
- Upgrade to paid plan for always-on service

### Environment Variables:
- Never commit `.env` file to Git
- Add all sensitive keys in Render dashboard
- Use Render's environment variable encryption

### Monitoring:
- Check logs regularly in Render dashboard
- Set up alerts for deployment failures
- Monitor service health

### Troubleshooting:
1. **Build fails**: Check `requirements.txt` and Python version
2. **Service crashes**: Check logs for errors
3. **CORS errors**: Update CORS settings in `main.py`
4. **Database connection**: Verify Supabase credentials
5. **Slow responses**: Consider upgrading plan

## Quick Deploy Checklist
- [ ] Code committed to Git
- [ ] `render.yaml` in backend folder
- [ ] `requirements.txt` updated
- [ ] Environment variables set in Render
- [ ] CORS updated for production
- [ ] Frontend API URL updated
- [ ] Test deployment

## Support
- Render Docs: https://render.com/docs
- Render Status: https://status.render.com
