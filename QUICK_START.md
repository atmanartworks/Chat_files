# Quick Start Guide

## 🚀 Getting Started

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Activate virtual environment:
```bash
# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

3. Start the backend server:
```bash
uvicorn app.main:app --reload
```

Backend will run on `http://127.0.0.1:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies (if not already done):
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

Frontend will run on `http://localhost:5173`

## 📋 Usage

1. **Upload a Document**: 
   - Click "Choose File" and select a PDF, TXT, or DOCX file
   - Click "Upload & Process"

2. **Chat with Document**:
   - Type your question in the chat input
   - Press Enter or click Send
   - Get AI-powered answers based on your document

3. **Generate PDF**:
   - Check "Generate PDF" checkbox before sending a message
   - After getting a response, click "Download PDF" to download

## 🛠️ Features

- ✅ File upload (PDF, TXT, DOCX)
- ✅ Document processing with RAG
- ✅ Chat interface
- ✅ PDF generation
- ✅ Modern, responsive UI
- ✅ Error handling

## 🔧 Troubleshooting

- **CORS Error**: Make sure backend is running and CORS is configured
- **File Upload Fails**: Check file format (PDF, TXT, or DOCX only)
- **Chat Not Working**: Ensure a document is uploaded first
- **PDF Generation Fails**: Check backend logs for errors
