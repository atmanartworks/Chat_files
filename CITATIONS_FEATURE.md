# 📚 Citations Feature - Complete Guide

## ✅ Citations Implemented!

Your application now includes **automatic citation generation** for all RAG-based responses!

---

## 🎯 What Are Citations?

Citations show **where the information came from** in your uploaded documents:
- **Document name** (filename)
- **Page numbers** (for PDFs)
- **Source references** (numbered citations)

---

## 🔧 How It Works

### **1. Automatic Citation Extraction**

When you ask a question about an uploaded document:

1. **System retrieves** relevant document chunks
2. **Extracts metadata** (page numbers, source file)
3. **Generates citations** automatically
4. **Displays sources** below the answer

### **2. Citation Format**

**In Response:**
```
[Your answer here...]

**Sources:**
[1] document.pdf, Page 3
[2] document.pdf, Page 5
[3] document.pdf, Page 7
```

**In Frontend:**
- Clean, formatted citation box
- Numbered references
- Page numbers highlighted
- Easy to read

---

## 📊 Database Storage

Citations are stored in the database:
- **Table:** `chat_history`
- **Column:** `citations` (JSON string)
- **Format:** List of citation objects

**Citation Object:**
```json
{
  "id": 1,
  "source": "document.pdf",
  "page": 3,
  "snippet": "First 100 chars of content..."
}
```

---

## 🎨 Frontend Display

Citations appear as a **styled box** below each answer:

```
📚 Sources:
[1] document.pdf, Page 3
[2] document.pdf, Page 5
```

**Features:**
- Clean, professional design
- Numbered references
- Page numbers in italic
- Light gray background
- Blue left border

---

## 💡 Usage Examples

### **Example 1: Ask a Question**
```
User: "What is mentioned about Python?"
```

**Response:**
```
Python is a high-level programming language...

**Sources:**
[1] resume.pdf, Page 2
[2] resume.pdf, Page 3
```

### **Example 2: Multiple Sources**
When information comes from multiple pages, all are cited:
```
**Sources:**
[1] document.pdf, Page 1
[2] document.pdf, Page 3
[3] document.pdf, Page 5
```

---

## 🔍 Technical Details

### **Backend Implementation**

1. **Citation Extraction** (`citations.py`):
   - Extracts metadata from retrieved documents
   - Creates citation objects
   - Formats citations for display

2. **RAG Integration** (`rag.py`):
   - `get_answer_with_sources()` function
   - Returns both answer and source documents
   - Preserves metadata for citations

3. **Response Formatting** (`main.py`):
   - Adds citations to answer text
   - Includes citations in JSON response
   - Saves to database

### **Frontend Implementation**

1. **Citation Display** (`ChatInterface.jsx`):
   - Renders citation box
   - Shows numbered references
   - Displays page numbers

2. **Styling** (`ChatInterface.css`):
   - Professional citation box design
   - Clean typography
   - Visual hierarchy

---

## 📋 Citation Features

✅ **Automatic** - No manual work needed
✅ **Page Numbers** - Exact page references
✅ **Source Files** - Document names
✅ **Numbered** - Easy to reference
✅ **Database Storage** - All citations saved
✅ **Visual Display** - Clean, readable format

---

## 🚀 Benefits

1. **Transparency** - Users know where info came from
2. **Verification** - Can check original sources
3. **Academic Style** - Professional citation format
4. **Trust** - Shows information is document-based
5. **Traceability** - Can find exact pages

---

## 📝 Response Format

**API Response:**
```json
{
  "answer": "Python is a programming language...\n\n**Sources:**\n[1] resume.pdf, Page 2",
  "mode": "rag",
  "citations": [
    {
      "id": 1,
      "source": "resume.pdf",
      "page": 2,
      "snippet": "Python programming experience..."
    }
  ]
}
```

---

## ✨ Summary

✅ **Citations automatically added** to all RAG responses
✅ **Page numbers** and source files included
✅ **Database storage** for citation history
✅ **Frontend display** with clean formatting
✅ **Professional format** for academic use

**Your application now has full citation support!** 📚✨
