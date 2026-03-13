from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from config import Config

def ingest_code():
    # Load the buggy code for indexing
    loader = TextLoader("demo/broken_code.py")
    docs = loader.load()

    # Split code by Python syntax to keep functions intact
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, chunk_size=500, chunk_overlap=50
    )
    split_docs = splitter.split_documents(docs)

    # Initialize Gemini Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    # Create and save the index
    vectorstore = FAISS.from_documents(split_docs, embeddings)
    vectorstore.save_local(Config.VECTORSTORE_PATH)
    print(f"✅ Code indexed successfully in {Config.VECTORSTORE_PATH}")

def retrieve_context(query):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectorstore = FAISS.load_local(Config.VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)
    return vectorstore.similarity_search(query, k=2)