# FounderGPT Backend API

FastAPI backend for FounderGPT - A ChatGPT-like application with RAG (Retrieval-Augmented Generation) capabilities.

## 🚀 Quick Start

### Local Development

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload
```

Server will run on `http://127.0.0.1:8000`

### API Documentation

Once running, visit:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 📋 Features

- ✅ User Authentication (JWT)
- ✅ File Upload & Management (Vault)
- ✅ RAG-based Q&A with Citations
- ✅ Direct LLM Generation
- ✅ PDF Generation
- ✅ Keyword Search
- ✅ Chat History
- ✅ Multi-user Support
- ✅ Supabase Integration
- ✅ Qdrant Vector Store

## 🔧 Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Supabase
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key

# Qdrant
QDRANT_URL=your-qdrant-url
QDRANT_API_KEY=your-qdrant-api-key

# LLM
GROQ_API_KEY=your-groq-api-key

# JWT
SECRET_KEY=your-secret-key

# Database (Optional - if using Supabase)
DATABASE_URL=your-postgresql-connection-string
```

## 📦 Dependencies

See `requirements.txt` for full list.

Key dependencies:
- FastAPI - Web framework
- Uvicorn - ASGI server
- LangChain - LLM framework
- Supabase - Database & Storage
- Qdrant - Vector database
- Groq - LLM provider

## 🌐 Deployment

### Render.com

See `RENDER_DEPLOYMENT_GUIDE.md` for complete deployment instructions.

Quick steps:
1. Push code to GitHub
2. Create Web Service on Render
3. Set environment variables
4. Deploy!

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py           # FastAPI app & routes
│   ├── auth.py           # Authentication
│   ├── database.py       # Database models
│   ├── vectorstore.py    # Vector store management
│   ├── rag.py            # RAG chain
│   ├── generator.py      # Direct generation
│   ├── loaders.py        # Document loaders
│   ├── supabase_*.py     # Supabase helpers
│   └── ...
├── requirements.txt      # Python dependencies
├── render.yaml          # Render configuration
├── Procfile             # Process file
└── README.md            # This file
```

## 🔐 API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /login` - Login and get token
- `GET /me` - Get current user info

### Vault (File Management)
- `POST /vault/upload` - Upload file
- `GET /vault/files` - Get all files
- `DELETE /vault/files/{id}` - Delete file
- `POST /vault/rebuild-vectorstore` - Rebuild vectorstore

### Chat
- `POST /chat` - Chat with documents (streaming)
- `GET /chat-history` - Get chat history

### Utilities
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - API documentation

## 🛠️ Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Style

```bash
# Format code
black app/

# Lint code
flake8 app/
```

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

## 📞 Support

For issues or questions, please open an issue on GitHub.
