import requests
import json
from config import Config

def test_ollama():
    print("--- LogicFlow Infrastructure Check: Ollama ---")
    print(f"Target URL: {Config.OLLAMA_BASE_URL}/api/generate")
    print(f"Target Model: {Config.OLLAMA_MODEL}")
    
    payload = {
        "model": Config.OLLAMA_MODEL,
        "prompt": "System Check: Infrastructure stabilized. Respond with 'Oracle Online'.",
        "stream": True,
        "options": {"num_predict": 50, "temperature": 0.1}
    }
    
    try:
        print("[*] Waiting for Ollama to start generating...")
        response = requests.post(f"{Config.OLLAMA_BASE_URL}/api/generate", json=payload, stream=True)
        response.raise_for_status()
        
        print("[OK] Connection Successful. Response: ", end="", flush=True)
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                print(data.get("response", ""), end="", flush=True)
        print() # newline at the end
    except requests.exceptions.ConnectionError:
        print(f"[FAIL] Connection Error: Ensure Ollama is running and accessible at {Config.OLLAMA_BASE_URL}")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

if __name__ == "__main__":
    test_ollama()
