# 🖥️ Ollama GPU Usage Information

## 📊 Current Status

### Project la Ollama GPU Configuration:

**Current Setup:**
- ✅ Ollama installed (`requirements.txt` la irukku)
- ✅ Ollama fallback option-ah use pannuthu (GROQ_API_KEY illana)
- ❌ **Explicit GPU configuration illa** - Ollama automatically GPU use pannum if available

### Code Analysis:

**File: `backend/app/llm.py`**
```python
# Ollama models tried (in order):
ollama_models = ["phi3:mini", "llama3", "llama2", "mistral", "phi3", "gemma"]

# GPU setting explicit-ah kodukkala - Ollama auto-detect pannum
return OllamaLLM(
    model=model,
    temperature=0.7,
    num_predict=500,
)
```

**File: `backend/app/vectorstore.py`**
```python
# Embeddings CPU la run aaguthu (GPU illa)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'},  # ⚠️ CPU use pannuthu
)
```

## 🎯 GPU Usage Details

### Ollama Models GPU Memory Requirements:

| Model | GPU Memory (Approx) | Speed |
|-------|---------------------|-------|
| **phi3:mini** | 2-3 GB | ⚡ Fastest |
| **llama3** | 4-6 GB | 🚀 Fast |
| **llama2** | 4-6 GB | 🚀 Fast |
| **mistral** | 5-7 GB | ⚡ Fast |
| **phi3** | 3-4 GB | ⚡ Fast |
| **gemma** | 4-6 GB | 🚀 Fast |

### Current Behavior:

1. **Ollama Service:**
   - Ollama automatically GPU use pannum if GPU available
   - GPU illana CPU la run aagum
   - No explicit configuration in code

2. **Embeddings:**
   - Currently **CPU only** (`device: 'cpu'`)
   - GPU use pannala

3. **Render Deployment:**
   - Render free tier la **GPU illa** - CPU only
   - Ollama local machine la run pannanum (Render la ollama service irukkaathu)

## 🔧 How to Check GPU Usage

### Local Machine la Check Pannum:

```bash
# Ollama service status check
ollama list

# GPU usage check (if NVIDIA GPU iruntha)
nvidia-smi

# Ollama models pull pannum
ollama pull phi3:mini
ollama pull llama3
```

### GPU Available-ah Check Pannum:

```python
# Python la check pannum
import torch
print(f"CUDA Available: {torch.cuda.is_available()}")
print(f"GPU Count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"GPU Name: {torch.cuda.get_device_name(0)}")
```

## ⚙️ GPU Configuration Options

### Option 1: Ollama la GPU Explicit-ah Set Pannum

Ollama service start pannumbodhu GPU specify pannalam:

```bash
# Environment variable set pannum
export OLLAMA_NUM_GPU=1
export CUDA_VISIBLE_DEVICES=0

# Ollama service start
ollama serve
```

### Option 2: Code la GPU Check Add Pannum

`backend/app/llm.py` la modify pannalam:

```python
import torch

def get_llm():
    # Check GPU availability
    use_gpu = torch.cuda.is_available()
    device_info = f"GPU: {torch.cuda.get_device_name(0)}" if use_gpu else "CPU"
    print(f"Using {device_info}")
    
    # Rest of the code...
```

### Option 3: Embeddings-ku GPU Use Pannum

`backend/app/vectorstore.py` la change pannum:

```python
import torch

# GPU available-ah check pannum
device = 'cuda' if torch.cuda.is_available() else 'cpu'

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': device},  # GPU use pannum if available
    encode_kwargs={'normalize_embeddings': False}
)
```

## 📝 Summary

### Current GPU Usage:
- **Ollama**: Auto-detect (GPU available-ah iruntha use pannum)
- **Embeddings**: CPU only (explicit-ah set pannirukku)
- **Render Deployment**: GPU illa (CPU only)

### Recommendations:

1. **Local Development:**
   - GPU iruntha, Ollama automatically use pannum
   - Embeddings-ku GPU enable pannalam (faster)

2. **Render Deployment:**
   - Render la GPU support illa
   - Ollama local machine la run pannanum
   - OR Groq API use pannum (cloud-based, faster)

3. **Production:**
   - Groq API recommend pannuthu (faster, no GPU needed)
   - Ollama local/GPU server la run pannalam

## 🚀 Next Steps

1. **GPU Check Pannum:**
   ```bash
   nvidia-smi  # GPU available-ah check
   ```

2. **Ollama Models Pull Pannum:**
   ```bash
   ollama pull phi3:mini  # Smallest, fastest model
   ```

3. **GPU Usage Monitor Pannum:**
   ```bash
   watch -n 1 nvidia-smi  # Real-time GPU usage
   ```

---

**Note**: Render la deploy pannumbodhu, Ollama local machine la run pannanum. Render la Ollama service install pannala. Groq API use pannumbodhu GPU need illa - cloud-based service.
