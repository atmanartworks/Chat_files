from langchain_huggingface import HuggingFaceEmbeddings  # type: ignore
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv  # type: ignore

# Load environment variables from .env file
load_dotenv()

# Optional Qdrant imports (only if using Qdrant Cloud)
QDRANT_AVAILABLE = False
Qdrant = None
QdrantClient = None
try:
    from qdrant_client import QdrantClient  # type: ignore
    from qdrant_client.http import models  # type: ignore
    try:
        from langchain_qdrant import QdrantVectorStore  # type: ignore
        Qdrant = QdrantVectorStore
        USING_NEW_QDRANT = True
    except ImportError:
        # Fallback to deprecated version
        from langchain_community.vectorstores import Qdrant  # type: ignore
        USING_NEW_QDRANT = False
        print("Note: Using langchain_community.vectorstores.Qdrant (langchain-qdrant not installed)")
    QDRANT_AVAILABLE = True
except ImportError:
    print("Note: Qdrant not available. Install qdrant-client and langchain-qdrant if using Qdrant Cloud.")

# Use fast, lightweight embeddings (langchain-huggingface handles this efficiently)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'},  # Faster on CPU for small models
    encode_kwargs={'normalize_embeddings': False}  # Skip normalization for speed
)

# Qdrant Cloud Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "")  # Your Qdrant Cloud URL
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")  # Your Qdrant Cloud API Key

# Debug: Print if credentials are loaded
if QDRANT_URL and QDRANT_API_KEY:
    print(f"Qdrant Cloud configured: URL={QDRANT_URL[:50]}...")
else:
    print("Warning: QDRANT_URL and QDRANT_API_KEY not found in environment variables. Using local Qdrant.")

def get_qdrant_client():
    """Get Qdrant client (cloud or local)."""
    if not QDRANT_AVAILABLE:
        raise RuntimeError(
            "Qdrant is not available. Install qdrant-client package. "
            "Or set QDRANT_URL and QDRANT_API_KEY to use Qdrant Cloud."
        )
    
    if QDRANT_URL and QDRANT_API_KEY:
        # Use Qdrant Cloud
        return QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )
    else:
        # Fallback to local Qdrant (for development)
        print("Warning: QDRANT_URL and QDRANT_API_KEY not set. Using local Qdrant.")
        return QdrantClient(location=":memory:")

def get_collection_name(user_id: int) -> str:
    """Get collection name for user."""
    return f"user_{user_id}_documents"

def create_vectorstore(docs, user_id: int):
    """Create a new vectorstore from documents using Qdrant Cloud."""
    # Use smaller chunks for faster retrieval
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # Smaller chunks = faster processing
        chunk_overlap=50,
        length_function=len,
    )
    
    # Split documents into smaller chunks
    split_docs = text_splitter.split_documents(docs)
    
    # Ensure metadata includes source and page information for citations
    for i, doc in enumerate(split_docs):
        if not hasattr(doc, 'metadata') or not doc.metadata:
            doc.metadata = {}
        
        # Preserve source information
        if 'source' not in doc.metadata:
            # Try to extract from original metadata or use index
            doc.metadata['source'] = doc.metadata.get('source', f'Document_{i+1}')
        
        # Ensure page number is preserved
        if 'page' not in doc.metadata and hasattr(doc, 'metadata'):
            # Try to get from original docs
            for orig_doc in docs:
                if hasattr(orig_doc, 'metadata') and orig_doc.metadata.get('page'):
                    doc.metadata['page'] = orig_doc.metadata.get('page')
                    break
    
    # Create Qdrant vectorstore
    if not QDRANT_AVAILABLE or Qdrant is None:
        raise RuntimeError(
            "Qdrant is required for vectorstore. Please install qdrant-client and langchain-qdrant packages, "
            "or set QDRANT_URL and QDRANT_API_KEY to use Qdrant Cloud."
        )
    
    collection_name = get_collection_name(user_id)
    client = get_qdrant_client()
    
    # Create vectorstore manually to avoid from_documents init_from parameter issue
    try:
        # Check if collection exists
        collections = client.get_collections().collections
        collection_exists = any(col.name == collection_name for col in collections)
        
        if not collection_exists:
            # Create collection manually
            from qdrant_client.http import models as rest
            # Get embedding dimension (all-MiniLM-L6-v2 has 384 dimensions)
            # Test with first document to get embedding size
            test_embedding = embeddings.embed_query("test")
            vector_size = len(test_embedding)
            
            try:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=rest.VectorParams(
                        size=vector_size,
                        distance=rest.Distance.COSINE
                    )
                )
                print(f"Created Qdrant collection: {collection_name}")
            except Exception as e:
                # Collection might have been created by another process
                if "already exists" not in str(e).lower():
                    print(f"Warning: Error creating collection (might already exist): {e}")
        
        # Create Qdrant instance with existing client
        vectorstore = Qdrant(client, collection_name, embeddings)
        
        # Add documents to the vectorstore
        vectorstore.add_documents(split_docs)
        
    except Exception as e:
        print(f"Error creating Qdrant vectorstore: {e}")
        raise
    
    print(f"Created Qdrant vectorstore for user {user_id} in collection: {collection_name}")
    return vectorstore

def load_vectorstore(user_id: int):
    """Load vectorstore from Qdrant Cloud or local."""
    try:
        collection_name = get_collection_name(user_id)
        
        if QDRANT_URL and QDRANT_API_KEY:
            # Load from Qdrant Cloud
            client = get_qdrant_client()
            # Check if collection exists
            collections = client.get_collections().collections
            collection_exists = any(col.name == collection_name for col in collections)
            
            if collection_exists:
                # Load existing collection
                # Qdrant __init__ takes positional args: (client, collection_name, embeddings)
                vectorstore = Qdrant(
                    client,
                    collection_name,
                    embeddings,
                )
                print(f"Loaded Qdrant vectorstore for user {user_id} from collection: {collection_name}")
                return vectorstore
            else:
                print(f"No Qdrant collection found for user {user_id}")
                return None
        else:
            # Local Qdrant (in-memory) - collections don't persist, return None to rebuild
            print(f"Local Qdrant mode - collections are in-memory only, will rebuild")
            return None
    except Exception as e:
        print(f"Error loading Qdrant vectorstore for user {user_id}: {e}")
        return None

def save_vectorstore(vectorstore, user_id: int):
    """Save vectorstore to Qdrant Cloud (already saved, just confirm)."""
    # Qdrant automatically persists to cloud, so this is just a confirmation
    try:
        collection_name = get_collection_name(user_id)
        print(f"Vectorstore for user {user_id} is saved in Qdrant Cloud collection: {collection_name}")
        return True
    except Exception as e:
        print(f"Error confirming Qdrant vectorstore save for user {user_id}: {e}")
        return False

def delete_vectorstore(user_id: int):
    """Delete vectorstore from Qdrant Cloud."""
    try:
        collection_name = get_collection_name(user_id)
        client = get_qdrant_client()
        
        # Check if collection exists
        collections = client.get_collections().collections
        collection_exists = any(col.name == collection_name for col in collections)
        
        if collection_exists:
            client.delete_collection(collection_name)
            print(f"Deleted Qdrant collection for user {user_id}: {collection_name}")
            return True
        else:
            print(f"Collection {collection_name} does not exist for user {user_id}")
            return False
    except Exception as e:
        print(f"Error deleting Qdrant vectorstore for user {user_id}: {e}")
        return False

def add_documents_to_vectorstore(vectorstore, docs, user_id: int):
    """Add new documents to existing Qdrant vectorstore."""
    try:
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
        )
        split_docs = text_splitter.split_documents(docs)
        
        # Ensure metadata
        for i, doc in enumerate(split_docs):
            if not hasattr(doc, 'metadata') or not doc.metadata:
                doc.metadata = {}
            if 'source' not in doc.metadata:
                doc.metadata['source'] = doc.metadata.get('source', f'Document_{i+1}')
        
        # Add documents to existing vectorstore
        vectorstore.add_documents(split_docs)
        print(f"Added documents to Qdrant vectorstore for user {user_id}")
        return True
    except Exception as e:
        print(f"Error adding documents to Qdrant vectorstore for user {user_id}: {e}")
        return False
