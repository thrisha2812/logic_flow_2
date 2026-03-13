import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load your key from .env
load_dotenv()

def initialize_archeologist():
    try:
        # Initialize with explicit V1 Stable configuration
        client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY"),
            http_options=types.HttpOptions(api_version='v1')
        )
        
        # MARCH 2026 PRO-TIP: Use the 'gemini-3-flash' alias for stability
        # or 'gemini-3.1-flash-001' for a version-locked instance.
        model_id = "gemini-3-flash" 
        
        response = client.models.generate_content(
            model=model_id,
            contents="System Check: Infrastructure stabilized. Respond with 'Oracle Online'."
        )
        
        print(f"✅ Connection Successful: {response.text}")
        return client
    except Exception as e:
        print(f"❌ Setup Error: {e}")
        return None

if __name__ == "__main__":
    initialize_archeologist()