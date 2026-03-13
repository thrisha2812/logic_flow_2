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

# Professional logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LogicFlow")

class DigitalArcheologist:
    def __init__(self):
        """
        Initializes the LogicFlow Agent. 
        Removed v1 restriction to ensure 2026 Preview models (Gemini 3) work.
        """
        try:
            self.client = genai.Client(
                api_key=os.getenv("GOOGLE_API_KEY")
            )
            # March 2026 Stable/Preview Workhorses
            self.available_models = ["gemini-3-flash-preview", "gemini-3.1-pro-preview"]
            logger.info(f"LogicFlow Pipeline Architect active.")
        except Exception as e:
            logger.error(f"Critical initialization failure: {e}")

    def excavate_and_repair(self, issue_id, broken_code):
        """
        The Core Agentic Loop: Excavate -> Restore -> Stabilize.
        """
        # 1. EXCAVATION
        logger.info(f"Excavating context for Issue #{issue_id}...")
        context_snippets = retrieve_context(broken_code[:100])
        context_str = "\n---\n".join([str(snippet) for snippet in context_snippets])

        # Updated prompt to force JSON for the explanation feature
        prompt = f"""
        Repair this Python artifact using the provided context.
        Return your response in STRICT JSON format with exactly two keys:
        1. 'code': The fixed Python code string.
        2. 'explanation': A brief technical description of how you solved the bug.

        CONTEXT FROM REPO:
        {context_str}

        BROKEN ARTIFACT:
        {broken_code}
        """

        # 2. RESTORATION
        for model_name in self.available_models:
            logger.info(f"Querying Oracle: {model_name}...")
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                
                if response and response.text:
                    # Parse the JSON response
                    ai_data = json.loads(response.text)
                    restored_code = ai_data.get('code', '')
                    explanation = ai_data.get('explanation', 'No explanation provided.')
                    
                    # 3. STABILIZATION (Docker Verification)
                    logger.info(f"Verifying restoration with {model_name} in Docker sandbox...")
                    success, test_log = run_isolated_test(restored_code)
                    
                    # If successful, we trigger the PR here or return it to the UI
                    pr_url = None
                    if success:
                        logger.info("Docker Check Passed. Opening Pull Request...")
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
                        "meta": {"model": model_name}
                    }

            except Exception as e:
                logger.warning(f"Oracle {model_name} failed: {str(e)[:100]}")
                continue

        return {
            "success": False, 
            "restored_code": "", 
            "test_log": "All Stable Oracles failed or Docker verification failed.",
            "pr_url": None
        }

# --- Initialization Logic for Streamlit ---
if 'archeologist' not in st.session_state:
    st.session_state.archeologist = DigitalArcheologist()

archeologist = st.session_state.archeologist