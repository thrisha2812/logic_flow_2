import os
import faiss
import numpy as np
import pickle
import logging
import requests
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LogicFlow.Memory")


class LogicFlowEmbedder:
    """Custom embedder to use local Ollama models."""

    def __init__(self, model=Config.OLLAMA_EMBED_MODEL):
        self.model = model
        self.base_url = Config.OLLAMA_BASE_URL
        self.timeout = Config.OLLAMA_TIMEOUT

    def _get_embedding(self, text):
        payload = {
            "model": self.model,
            "prompt": text,
        }
        response = requests.post(
            f"{self.base_url}/api/embeddings",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()["embedding"]

    def embed_documents(self, texts):
        return [np.array(self._get_embedding(t), dtype="float32") for t in texts]

    def embed_query(self, text):
        return np.array(self._get_embedding(text), dtype="float32")


def _read_demo_source():
    with open("demo/broken_code.py", "r", encoding="utf-8") as f:
        return f.read()


def _chunk_python_source(source, chunk_size=500, overlap=80):
    if not source.strip():
        return []

    lines = source.splitlines()
    chunks = []
    current = []
    current_len = 0

    for line in lines:
        line_len = len(line) + 1
        if current and current_len + line_len > chunk_size:
            chunks.append("\n".join(current).strip())

            overlap_lines = []
            overlap_len = 0
            for existing in reversed(current):
                overlap_lines.insert(0, existing)
                overlap_len += len(existing) + 1
                if overlap_len >= overlap:
                    break

            current = overlap_lines[:]
            current_len = sum(len(existing) + 1 for existing in current)

        current.append(line)
        current_len += line_len

    if current:
        chunks.append("\n".join(current).strip())

    return [chunk for chunk in chunks if chunk]


def ingest_code():
    """Wipes the old memory and creates a fresh, stable FAISS index."""
    source = _read_demo_source()
    texts = _chunk_python_source(source)

    if not texts:
        logger.warning("No source chunks found for ingestion.")
        return

    embedder = LogicFlowEmbedder()

    try:
        logger.info(f"Generating stable embeddings with {Config.OLLAMA_EMBED_MODEL}...")
        embeddings = embedder.embed_documents(texts)
        vectors = np.vstack(embeddings)

        dim = vectors.shape[1]
        index = faiss.IndexFlatIP(dim)
        faiss.normalize_L2(vectors)
        index.add(vectors)

        os.makedirs(Config.VECTORSTORE_PATH, exist_ok=True)

        index_file = os.path.join(Config.VECTORSTORE_PATH, "index.bin")
        meta_file = os.path.join(Config.VECTORSTORE_PATH, "meta.pkl")

        faiss.write_index(index, index_file)
        with open(meta_file, "wb") as f:
            pickle.dump(texts, f)

        logger.info(f"Memory stabilized at {Config.VECTORSTORE_PATH}")
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")


def retrieve_context(query):
    """Retrieves relevant code snippets using the stable pipeline."""
    embedder = LogicFlowEmbedder()

    index_file = os.path.join(Config.VECTORSTORE_PATH, "index.bin")
    meta_file = os.path.join(Config.VECTORSTORE_PATH, "meta.pkl")

    if not os.path.exists(index_file) or not os.path.exists(meta_file):
        logger.info("Vector store missing; ingesting code before retrieval.")
        ingest_code()

    index = faiss.read_index(index_file)
    with open(meta_file, "rb") as f:
        meta_texts = pickle.load(f)

    query_vec = embedder.embed_query(query).reshape(1, -1)
    faiss.normalize_L2(query_vec)

    distances, indices = index.search(query_vec, k=Config.RETRIEVE_TOP_K)
    return [meta_texts[i] for i in indices[0] if i != -1]
