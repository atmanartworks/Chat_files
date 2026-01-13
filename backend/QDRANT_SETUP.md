# Qdrant Cloud Setup Guide

## Step 1: Create Qdrant Cloud Account
1. Go to https://cloud.qdrant.io/
2. Sign up for a free account
3. Create a new cluster

## Step 2: Get Your Credentials
1. After creating cluster, you'll get:
   - **QDRANT_URL**: Your cluster URL (e.g., `https://xxxxx-xxxxx.qdrant.io`)
   - **QDRANT_API_KEY**: Your API key

## Step 3: Configure Environment Variables
Create or update `backend/.env` file:

```env
QDRANT_URL=https://your-cluster-id.qdrant.io
QDRANT_API_KEY=your-api-key-here
```

## Step 4: Install Dependencies
```bash
cd backend
pip install qdrant-client
```

## Step 5: Test Connection
The application will automatically connect to Qdrant Cloud on startup.

## Troubleshooting

### If QDRANT_URL and QDRANT_API_KEY are not set:
- The app will use in-memory Qdrant (for development only)
- Data will be lost on server restart
- **For production, always set Qdrant Cloud credentials**

### Common Issues:
1. **Connection Error**: Check your QDRANT_URL and QDRANT_API_KEY
2. **Authentication Error**: Verify your API key is correct
3. **Collection Not Found**: This is normal for new users - collections are created automatically

## How It Works:
- Each user gets a separate collection: `user_{user_id}_documents`
- Vectors are automatically saved to Qdrant Cloud
- No local disk storage needed
- Works with multiple backend servers
