import os
import faiss
import numpy as np
import pickle
import logging
from google import genai
from google.genai import types
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LogicFlow.Memory")

# Initialize the Stable Client
client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY"),
   
)

class LogicFlowEmbedder:
    """Custom embedder to ensure V1 Stable consistency with the 2026 registry."""
    def __init__(self, model="gemini-embedding-001"):
        self.model = model

    def embed_documents(self, texts):
        response = client.models.embed_content(
            model=self.model,
            contents=texts,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
        )
        return [np.array(emb.values, dtype="float32") for emb in response.embeddings]

    def embed_query(self, text):
        response = client.models.embed_content(
            model=self.model,
            contents=text,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
        )
        return np.array(response.embeddings[0].values, dtype="float32")

# --- ADD THESE FUNCTIONS TO THE FILE ---

def ingest_code():
    """Wipes the old memory and creates a fresh, stable FAISS index."""
    # 1. Load the target code
    loader = TextLoader("demo/broken_code.py")
    docs = loader.load()

    # 2. Split into logical chunks
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, chunk_size=500, chunk_overlap=50
    )
    split_docs = splitter.split_documents(docs)
    texts = [doc.page_content for doc in split_docs]

    embedder = LogicFlowEmbedder()
    
    try:
        logger.info("Generating stable embeddings with gemini-embedding-001...")
        embeddings = embedder.embed_documents(texts)
        vectors = np.vstack(embeddings)
        
        # --- THE MISSING PART: Define 'index' ---
        dim = vectors.shape[1] # Usually 3072 for gemini-embedding-001
        index = faiss.IndexFlatIP(dim) # <--- 'index' is defined here
        faiss.normalize_L2(vectors)
        index.add(vectors)
        # ----------------------------------------
        
        # Create the directory safely
        os.makedirs(Config.VECTORSTORE_PATH, exist_ok=True)
        
        # Define exact file paths
        index_file = os.path.join(Config.VECTORSTORE_PATH, "index.bin")
        meta_file = os.path.join(Config.VECTORSTORE_PATH, "meta.pkl")
        
        # Save the index and metadata
        faiss.write_index(index, index_file)
        with open(meta_file, "wb") as f:
            pickle.dump(texts, f)
            
        logger.info(f"✅ Memory stabilized at {Config.VECTORSTORE_PATH}")
    except Exception as e:
        logger.error(f"❌ Ingestion Failed: {e}")
    

def retrieve_context(query):
    """Retrieves relevant code snippets using the stable pipeline."""
    embedder = LogicFlowEmbedder()
    
    # --- MATCH THE NEW PATH LOGIC ---
    index_file = os.path.join(Config.VECTORSTORE_PATH, "index.bin")
    meta_file = os.path.join(Config.VECTORSTORE_PATH, "meta.pkl")
    
    # Load the index and the metadata
    index = faiss.read_index(index_file)
    with open(meta_file, "rb") as f:
        meta_texts = pickle.load(f)
    # --------------------------------

    # Embed the query and search
    query_vec = embedder.embed_query(query).reshape(1, -1)
    faiss.normalize_L2(query_vec)
    
    distances, indices = index.search(query_vec, k=2)
    return [meta_texts[i] for i in indices[0] if i != -1]