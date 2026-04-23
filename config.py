"""
Configuration - Updated for Local LLM support
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ==================== LLM Configuration ====================
    # Choose: "ollama" or "lmstudio"
    LLM_BACKEND = os.getenv("LLM_BACKEND", "ollama")
    
    # Model name (must match what you downloaded)
    # Recommended for code: "codellama", "deepseek-coder:6.7b", "qwen2.5-coder:7b"
    # Recommended for general: "llama3", "mistral"
    LLM_MODEL = os.getenv("LLM_MODEL", "codellama:7b-instruct-q2_K")
    
    # LLM Parameters
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4096"))
    
    # Ollama settings
    OLLAMA_BASE_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("LLM_MODEL", "codellama:7b-instruct-q2_K")
    OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    
    # LM Studio settings
    LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
    
    # ==================== LLM APIs Removed ====================
    # (Gemini dependency has been cleaned up)
    
    # ==================== Tool Configuration ====================
    # Docker settings
    DOCKER_ENABLED = os.getenv("DOCKER_ENABLED", "true").lower() == "true"
    DOCKER_TIMEOUT = int(os.getenv("DOCKER_TIMEOUT", "30"))
    
    # GitHub settings (if needed)
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_REPO=os.getenv("GITHUB_REPO","")
    
    # ==================== Vector Store ====================
    FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "vectorstore/faiss_index")
    VECTORSTORE_PATH = os.getenv("VECTORSTORE_PATH", "vectorstore/faiss_index")
    
    # ==================== Logging ====================
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # ==================== Agent Settings ====================
    MAX_CORRECTION_ITERATIONS = int(os.getenv("MAX_CORRECTION_ITERATIONS", "3"))
    VERBOSITY = os.getenv("VERBOSITY", "concise")


# Create singleton instance
config = Config()