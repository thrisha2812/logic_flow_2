import os
import logging
from google import genai
from google.genai import types
from config import Config
from tools.faiss_tool import retrieve_context
from tools.docker_test_tool import run_isolated_test

# Professional logging for your evaluation
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LogicFlow")

class DigitalArcheologist:
    def __init__(self):
        """
        Initializes the LogicFlow Agent with a focus on Stable V1.
        """
        try:
            # Mistake Prevention: Use api_version='v1' and no 'models/' prefix
            self.client = genai.Client(
                api_key=os.getenv("GOOGLE_API_KEY"),
               
            )
            # March 2026 Stable Workhorses
            self.available_models = ["gemini-3-flash-preview", "gemini-3.1-pro-preview"]
            logger.info(f"LogicFlow Pipeline Architect active. Intelligence: {self.available_models[0]}")
        except Exception as e:
            logger.error(f"Critical initialization failure: {e}")

    def excavate_and_repair(self, issue_id, broken_code):
        """
        The Core Agentic Loop: Excavate -> Restore -> Stabilize.
        """
        # 1. EXCAVATION (Retrieve from fresh FAISS index)
        logger.info(f"Excavating context for Issue #{issue_id}...")
        context_snippets = retrieve_context(broken_code[:100])
        context_str = "\n---\n".join([str(snippet) for snippet in context_snippets])

        prompt = f"""
        Repair this Python artifact.
        Return your response in JSON format with two keys:
        1. 'code': The fixed Python code.
        2. 'explanation': A brief technical description of how you solved the bug.

        BROKEN ARTIFACT:
        {broken_code}
        """

        # 2. RESTORATION (Failover Loop)
        for model_name in self.available_models:
            logger.info(f"Querying Oracle: {model_name}...")
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                
                if response and response.text:
                    # Clean the Markdown
                    content = response.text
                    restored_code = content.split("```python")[1].split("```")[0].strip() if "```python" in content else content.strip()
                    
                    # 3. STABILIZATION (Docker Verification)
                    logger.info(f"Verifying restoration with {model_name} in Docker sandbox...")
                    success, log = run_isolated_test(restored_code)
                    
                    return {
                        "success": success,
                        "restored_code": restored_code,
                        "test_log": log,
                        "meta": {"model": model_name, "api_version": "v1"}
                    }
            except Exception as e:
                logger.warning(f"Oracle {model_name} failed: {str(e)[:100]}")
                continue

        return {
            "success": False, 
            "restored_code": "", 
            "test_log": "All Stable Oracles failed. Infrastructure active, but Brain offline."
        }