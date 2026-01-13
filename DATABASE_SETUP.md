# Database Connection - Complete Setup

## ✅ Database Connected Successfully!

### Database Type: **SQLite**
- **File:** `chat_with_files.db` (created automatically)
- **Location:** `backend/` folder
- **No setup required** - Works out of the box!

---

## 📊 Database Tables

### 1. **chat_history**
Stores all chat conversations:
- `id` - Primary key
- `query` - User's question
- `response` - AI's answer
- `mode` - "rag" or "generation"
- `pdf_generated` - Boolean
- `pdf_url` - PDF download link
- `created_at` - Timestamp

### 2. **documents**
Stores uploaded document information:
- `id` - Primary key
- `filename` - Original filename
- `filepath` - File location
- `file_type` - pdf, txt, or docx
- `uploaded_at` - Timestamp
- `processed` - Boolean

### 3. **keyword_searches**
Stores keyword search history:
- `id` - Primary key
- `document_id` - Reference to document
- `keyword` - Searched keyword
- `occurrences` - Number of times found
- `locations` - JSON with page numbers and context
- `searched_at` - Timestamp

---

## 🔍 New Features Added

### 1. **Keyword Search in PDF**
Find exact locations where keywords appear in uploaded documents!

**Endpoint:** `POST /search-keyword`
```json
{
  "keyword": "indhumathi"
}
```

**Response:**
```json
{
  "keyword": "indhumathi",
  "occurrences": 5,
  "found": true,
  "pages": [1, 3, 5],
  "locations": [
    {
      "page": 1,
      "position": 245,
      "context": "...text before **indhumathi** text after...",
      "snippet": "Full context snippet"
    }
  ]
}
```

### 2. **Multiple Keyword Search**
Search for multiple keywords at once!

**Endpoint:** `POST /search-keywords`
```json
{
  "keywords": ["indhumathi", "python", "AI"]
}
```

### 3. **Chat History**
View all past conversations!

**Endpoint:** `GET /chat-history?skip=0&limit=50`

### 4. **Document List**
View all uploaded documents!

**Endpoint:** `GET /documents`

---

## 🚀 How to Use

### Search for Keyword in PDF:

1. **Upload a document** first via `/upload`
2. **Search for keyword:**
   ```bash
   POST /search-keyword
   {
     "keyword": "indhumathi"
   }
   ```
3. **Get results** with:
   - Exact page numbers
   - Context around each occurrence
   - Total count

### Example Usage:

```python
# After uploading a PDF
# Search for "indhumathi"
response = requests.post(
    "http://127.0.0.1:8000/search-keyword",
    json={"keyword": "indhumathi"}
)

result = response.json()
print(f"Found {result['occurrences']} times")
print(f"On pages: {result['pages']}")
for location in result['locations']:
    print(f"Page {location['page']}: {location['context']}")
```

---

## 📁 Database File

- **Location:** `backend/chat_with_files.db`
- **Type:** SQLite (file-based, no server needed)
- **Auto-created:** On first run
- **Backup:** Just copy the `.db` file

---

## ✅ Verification

Database is automatically initialized when you start the server:

```python
@app.on_event("startup")
async def startup_event():
    init_db()
    print("✅ Database connected and initialized!")
```

---

## 🎯 Benefits

1. **Persistent Storage** - Chat history saved
2. **Keyword Search** - Find exact locations in PDFs
3. **Document Tracking** - Know what files were uploaded
4. **Search History** - Track what keywords were searched
5. **No Setup** - SQLite works immediately

---

## 🔧 Database Management

### View Database:
```bash
# Install SQLite browser or use command line
sqlite3 backend/chat_with_files.db

# View tables
.tables

# View chat history
SELECT * FROM chat_history;

# View documents
SELECT * FROM documents;
```

### Reset Database:
```bash
# Delete database file
rm backend/chat_with_files.db

# Restart server - new database will be created
```

---

## ✨ Summary

✅ **Database:** SQLite (connected)
✅ **Auto-initialized:** On server start
✅ **Features:** Chat history, keyword search, document tracking
✅ **No configuration needed:** Works out of the box!

**Your application now has full database support!** 🎉
