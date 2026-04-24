"""
Configuration - Updated for Local LLM support
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    LLM_BACKEND = os.getenv("LLM_BACKEND", "ollama")
    LLM_MODEL = os.getenv("LLM_MODEL", "codellama:7b-instruct-q2_K")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1024"))

    OLLAMA_BASE_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("LLM_MODEL", "codellama:7b-instruct-q2_K")
    OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))

    LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")

    DOCKER_ENABLED = os.getenv("DOCKER_ENABLED", "true").lower() == "true"
    DOCKER_TIMEOUT = int(os.getenv("DOCKER_TIMEOUT", "30"))

    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_REPO = os.getenv("GITHUB_REPO", "")
    DEMO_CODE_PATH = os.getenv("DEMO_CODE_PATH", "demo/broken_code.py")

    FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "vectorstore/faiss_index")
    VECTORSTORE_PATH = os.getenv("VECTORSTORE_PATH", "vectorstore/faiss_index")
    RETRIEVE_TOP_K = int(os.getenv("RETRIEVE_TOP_K", "1"))
    MAX_CONTEXT_CHARS = int(os.getenv("MAX_CONTEXT_CHARS", "900"))
    MAX_BROKEN_CODE_CHARS = int(os.getenv("MAX_BROKEN_CODE_CHARS", "1600"))

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_CORRECTION_ITERATIONS = int(os.getenv("MAX_CORRECTION_ITERATIONS", "2"))
    VERBOSITY = os.getenv("VERBOSITY", "concise")


config = Config()
