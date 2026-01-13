# Render la Backend Deploy Pannum Step-by-Step Guide

## 🚀 Step 1: Git Repository Setup
1. GitHub/GitLab/Bitbucket la account create pannunga
2. Your project code-a commit pannunga
3. Repository create pannitu code-a push pannunga

## 🌐 Step 2: Render Account Create
1. https://render.com ku ponga
2. "Sign Up" click pannunga (GitHub account use pannalam)
3. Login pannunga

## 📦 Step 3: New Web Service Create
1. Render dashboard la "New +" button click pannunga
2. "Web Service" select pannunga
3. Your Git repository-a connect pannunga:
   - GitHub/GitLab/Bitbucket select pannunga
   - Render ku access koduthu
   - Your repository select pannunga

## ⚙️ Step 4: Service Configuration
1. **Name**: `foundergpt-backend` (enna name venumalum kodukalam)
2. **Region**: Singapore or US East (neenga eppadi close irukinga)
3. **Branch**: `main` or `master`
4. **Root Directory**: `backend` ⚠️ (Important - backend folder path)
5. **Runtime**: `Python 3`
6. **Build Command**: `pip install -r requirements.txt`
7. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 🔐 Step 5: Environment Variables Set Pannunga
"Advanced" section la click pannitu, intha variables add pannunga:

### Required Variables:
```
SUPABASE_URL = your-supabase-project-url
SUPABASE_KEY = your-supabase-anon-key
SUPABASE_SERVICE_KEY = your-supabase-service-role-key
QDRANT_URL = your-qdrant-cloud-url
QDRANT_API_KEY = your-qdrant-api-key
GROQ_API_KEY = your-groq-api-key
SECRET_KEY = (Render auto-generate pannum, or manually add)
DATABASE_URL = your-supabase-postgresql-connection-string
```

### Optional:
```
PYTHON_VERSION = 3.11.0
```

**Note**: `.env` file la irukura values-a copy pannitu Render la paste pannunga

## 🚢 Step 6: Deploy Start
1. "Create Web Service" button click pannunga
2. Render automatically build start pannum
3. 5-10 minutes wait pannunga
4. Logs check pannunga - errors iruntha fix pannunga

## 🌍 Step 7: CORS Settings Update
Deployment success aagumbodhu, `backend/app/main.py` la CORS update pannunga:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-domain.com",  # Neenga deploy panna frontend URL
        "http://localhost:5173",  # Local development
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🔗 Step 8: Backend URL Get
1. Deployment success aagumbodhu, URL kedaikkum:
   - Example: `https://foundergpt-backend.onrender.com`
2. Frontend la API base URL-a update pannunga:
   - `frontend/src/services/api.js` la base URL change pannunga

## ✅ Step 9: Test Pannunga
1. Browser la open pannunga: `https://your-backend-url.onrender.com/docs`
2. FastAPI documentation page varum
3. All endpoints test pannunga
4. Render dashboard la logs check pannunga

## ⚠️ Important Notes

### Free Tier Limitations:
- 15 minutes inactive iruntha service sleep aagum
- Sleep aagumbodhu first request 30-60 seconds eduthukum (cold start)
- Always-on venumna paid plan upgrade pannunga

### Environment Variables:
- `.env` file-a Git la commit pannadhinga
- All sensitive keys Render dashboard la add pannunga
- Render automatically encrypt pannum

### Monitoring:
- Regular ah logs check pannunga
- Deployment failures ku alerts set pannunga
- Service health monitor pannunga

## 🐛 Troubleshooting

### Build Fails:
- `requirements.txt` check pannunga
- Python version correct-a irukka check pannunga
- Logs la exact error paathu fix pannunga

### Service Crashes:
- Render dashboard la logs check pannunga
- Environment variables correct-a set pannirukka check pannunga
- Database connection verify pannunga

### CORS Errors:
- `main.py` la CORS settings update pannunga
- Frontend URL correct-a add pannirukka check pannunga

### Database Connection Issues:
- Supabase credentials verify pannunga
- Connection string correct-a irukka check pannunga

### Slow Responses:
- Free tier la cold start irukkum
- Paid plan upgrade pannunga for better performance

## 📋 Quick Checklist
- [ ] Code Git la commit pannirukka
- [ ] `render.yaml` backend folder la irukka
- [ ] `requirements.txt` updated
- [ ] Environment variables Render la set pannirukka
- [ ] CORS production ku update pannirukka
- [ ] Frontend API URL update pannirukka
- [ ] Deployment test pannirukka

## 📞 Support
- Render Documentation: https://render.com/docs
- Render Status: https://status.render.com
- Render Community: https://community.render.com

## 🎉 Success!
Deployment success aagumbodhu, your backend URL:
`https://your-service-name.onrender.com`

Frontend la intha URL use pannunga! 🚀
