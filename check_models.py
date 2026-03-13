import google.generativeai as genai
from config import Config

# Configure with your existing key
genai.configure(api_key=Config.GOOGLE_API_KEY)

print("Checking available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            # We print the name so you can copy-paste it exactly
            print(f"✅ Use this name: {m.name}")
except Exception as e:
    print(f"❌ Error connecting to Gemini: {e}")