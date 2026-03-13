import os
import logging
import json
import streamlit as st
from google import genai
from google.genai import types
from config import Config
from tools.faiss_tool import retrieve_context
from tools.docker_test_tool import run_isolated_test
from tools.github_tool import create_pull_request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LogicFlow")

class DigitalArcheologist:
    def __init__(self):
        try:
            self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
            self.available_models = ["gemini-3-flash-preview", "gemini-3.1-pro-preview"]
            logger.info("LogicFlow Pipeline Architect active.")
        except Exception as e:
            logger.error(f"Initialization failure: {e}")

    def excavate_and_repair(self, issue_id, broken_code):
        # 1. EXCAVATION
        context_snippets = retrieve_context(broken_code[:100])
        context_str = "\n---\n".join([str(snippet) for snippet in context_snippets])

        # 2. RESTORATION (Prompting for JSON)
        prompt = f"""
        Repair this Python artifact. Return STRICT JSON with keys 'code' and 'explanation'.
        CONTEXT: {context_str}
        BROKEN ARTIFACT: {broken_code}
        """

        for model_name in self.available_models:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                
                if response and response.text:
                    ai_data = json.loads(response.text)
                    restored_code = ai_data.get('code', '')
                    explanation = ai_data.get('explanation', 'No explanation provided.')
                    
                    # 3. STABILIZATION
                    success, test_log = run_isolated_test(restored_code)
                    
                    pr_url = None
                    if success:
                        pr_url = create_pull_request(
                            issue_id=issue_id,
                            fixed_code=restored_code,
                            file_path=Config.DEMO_CODE_PATH,
                            explanation=explanation
                        )

                    return {
                        "success": success,
                        "restored_code": restored_code,
                        "explanation": explanation,
                        "test_log": test_log,
                        "pr_url": pr_url,
                        "model_used": model_name
                    }
            except Exception as e:
                logger.warning(f"{model_name} failed: {e}")
                continue

        return {"success": False, "test_log": "All restoration attempts failed."}