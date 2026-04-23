"""
Local LLM Client - Works with Ollama and LM Studio
"""
import requests
import json
from typing import Optional, List, Dict, Any
from utils.logger import logger


class LocalLLMClient:
    """Client for local LLMs (Ollama/LM Studio compatible)"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "codellama",
        temperature: float = 0.1,
        max_tokens: int = 4096,
        timeout: int = 120
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        
    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict:
        """Make HTTP request to local LLM"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to LLM at {url}. "
                f"Make sure Ollama/LM Studio is running."
            )
        except requests.exceptions.Timeout:
            raise TimeoutError(f"LLM request timed out after {self.timeout}s")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate completion from prompt"""
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user", 
            "content": prompt
        })
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature or self.temperature,
                "num_predict": max_tokens or self.max_tokens
            }
        }
        
        logger.info(f"Sending request to {self.model}...")
        result = self._make_request("/api/chat", payload)
        
        if "message" in result:
            return result["message"]["content"]
        elif "response" in result:
            return result["response"]
        else:
            raise ValueError(f"Unexpected response format: {result}")
    
    def generate_with_history(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate with conversation history"""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature or self.temperature,
                "num_predict": max_tokens or self.max_tokens
            }
        }
        
        result = self._make_request("/api/chat", payload)
        return result.get("message", {}).get("content", "")
    
    def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ):
        """Stream generation (for real-time output)"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }
        
        url = f"{self.base_url}/api/chat"
        response = requests.post(url, json=payload, stream=True, timeout=self.timeout)
        
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "message" in data:
                    content = data["message"].get("content", "")
                    if content:
                        yield content
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            result = self._make_request("/api/tags", {})
            return [m["name"] for m in result.get("models", [])]
        except:
            return []
    
    def test_connection(self) -> bool:
        """Test if LLM is accessible"""
        try:
            models = self.list_models()
            return len(models) > 0
        except:
            return False


# LM Studio compatible client (uses OpenAI API format)
class LMStudioClient(LocalLLMClient):
    """Client specifically for LM Studio (OpenAI-compatible API)"""
    
    def __init__(self, base_url: str = "http://localhost:1234/v1", **kwargs):
        super().__init__(base_url=base_url, **kwargs)
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate using OpenAI-compatible API"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens
        }
        
        result = self._make_request("/chat/completions", payload)
        return result["choices"][0]["message"]["content"]


def get_llm_client(config) -> LocalLLMClient:
    """Factory function to get appropriate LLM client"""
    if config.LLM_BACKEND == "lmstudio":
        return LMStudioClient(
            base_url=config.LM_STUDIO_URL,
            model=config.LLM_MODEL,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=config.LLM_MAX_TOKENS
        )
    else:  # Default to Ollama
        return LocalLLMClient(
            base_url=config.OLLAMA_URL,
            model=config.LLM_MODEL,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=config.LLM_MAX_TOKENS
        )