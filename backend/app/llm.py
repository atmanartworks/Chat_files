from langchain_groq import ChatGroq  # type: ignore
import os

# Optional Ollama import (only for local development)
try:
    from langchain_ollama import OllamaLLM  # type: ignore
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Note: Ollama not available (optional - only for local development)")

def get_llm():
    # Try Groq first if API key is available (fastest option - works on Render)
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        try:
            return ChatGroq(
                api_key=groq_api_key,
                model="llama-3.1-8b-instant",  # Updated to supported model (replaces deprecated llama3-8b-8192)
                temperature=0.7,  # Balanced creativity/speed
                max_tokens=1000,  # Limit response length for speed
            )
        except Exception as e:
            print(f"Warning: Failed to initialize Groq LLM: {e}")
    
    # Fallback to Ollama if Groq is not available AND Ollama is installed
    if not OLLAMA_AVAILABLE:
        raise RuntimeError(
            "GROQ_API_KEY is required. Please set GROQ_API_KEY environment variable. "
            "Ollama is not available (optional package for local development only)."
        )
    
    # Try fastest models first
    ollama_models = ["phi3:mini", "llama3", "llama2", "mistral", "phi3", "gemma"]
    
    for model in ollama_models:
        try:
            return OllamaLLM(
                model=model,
                temperature=0.7,
                num_predict=500,  # Limit tokens for faster response
            )
        except Exception as e:
            error_str = str(e)
            # If model not found, try next model
            if "not found" in error_str.lower() or "404" in error_str:
                continue
            # If it's a connection error, raise it
            if "connection" in error_str.lower() or "refused" in error_str.lower():
                raise RuntimeError(
                    f"Ollama service is not running. Error: {error_str}. "
                    f"Please start Ollama service or set GROQ_API_KEY environment variable."
                )
            # For other errors, raise them
            raise RuntimeError(f"Failed to initialize Ollama with model '{model}': {error_str}")
    
    # If all models failed, provide helpful error message
    raise RuntimeError(
        f"Failed to initialize any LLM. Groq API key not set and none of the Ollama models are available. "
        f"Available models to try: {', '.join(ollama_models)}. "
        f"Please install a model using: ollama pull <model_name> "
        f"or set GROQ_API_KEY environment variable."
    )
