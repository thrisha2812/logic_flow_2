import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_REPO = os.getenv("GITHUB_REPO")
    VECTORSTORE_PATH = "vectorstore/logicflow_index"
    DEMO_CODE_PATH = "demo/broken_code.py"
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash")