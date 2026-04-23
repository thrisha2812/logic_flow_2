import os
import logging
import json
import requests
import streamlit as st
from config import Config
from tools.faiss_tool import retrieve_context
from tools.docker_test_tool import run_isolated_test
from tools.github_tool import create_pull_request

# Professional logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LogicFlow")

class DigitalArcheologist:
    def __init__(self):
        """Initializes the LogicFlow AI with access to local Ollama models."""
        try:
            self.base_url = Config.OLLAMA_BASE_URL
            self.model = Config.OLLAMA_MODEL
            # Ensure Ollama is reachable
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            logger.info(f"LogicFlow Pipeline Architect active. Connected to Ollama at {self.base_url}")
        except Exception as e:
            logger.error(f"Initialization failure (Ollama not reachable): {e}")

    def review_restoration(self, code, explanation):
        """
        Acts as a Senior Lead Developer. 
        Includes a failover to Flash if the Pro quota is reached.
        """
        review_prompt = f"""
        Review this proposed Python fix for security, efficiency, and PEP8 standards.
        PROPOSED CODE:
        {code}

        AI EXPLANATION:
        {explanation}

        Provide a critical review. If there are no issues, start with 'LGTM' (Looks Good To Me).
        """
        
        try:
            logger.info(f"Attempting Senior Peer Review with {self.model}...")
            payload = {
                "model": self.model,
                "prompt": review_prompt,
                "stream": False
            }
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get("response", "Review unavailable.")
            
        except Exception as e:
            return f"Review system failed: {e}"

    def excavate_and_repair(self, issue_id, broken_code, github_issue_text=None):
        """
        The Core Loop: 
        1. Excavate (RAG) 
        2. Restore (Fix based on GitHub Issue) 
        3. Stabilize (Docker) 
        4. Review (Multi-Agent) 
        5. Report (PR)
        """
        # 1. EXCAVATION (Search context using the Human's Bug Description)
        search_query = github_issue_text if github_issue_text else broken_code[:100]
        context_snippets = retrieve_context(search_query)
        context_str = "\n---\n".join([str(snippet) for snippet in context_snippets])

        # 2. RESTORATION (The 'Intent-Driven' Prompt)
        # This allows the AI to fix specific bugs described by the dev on GitHub
        prompt = f"""
        GITHUB ISSUE DESCRIPTION (#{issue_id}):
        {github_issue_text if github_issue_text else 'Generic bug repair.'}

        TASK:
        Repair the Python artifact below to satisfy the developer's request. 
        Use the provided repo context for logic consistency.
        Return STRICT JSON with keys 'code' and 'explanation'.

        CONTEXT:
        {context_str}

        BROKEN ARTIFACT:
        {broken_code}
        """

        try:
            logger.info(f"Querying Oracle: {self.model}...")
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=120)
            response.raise_for_status()
            
            response_data = response.json()
            if "response" in response_data:
                try:
                    ai_data = json.loads(response_data["response"])
                except json.JSONDecodeError:
                    ai_data = {}
                restored_code = ai_data.get('code', '')
                explanation = ai_data.get('explanation', 'No explanation provided.')
                    
                # 3. STABILIZATION (Docker Verification)
                logger.info("Verifying restoration in Docker sandbox...")
                success, test_log = run_isolated_test(restored_code)
                
                pr_url = None
                review_comments = "No review performed."
                
                if success:
                    # 4. MULTI-AGENT REVIEW (The Critic)
                    review_comments = self.review_restoration(restored_code, explanation)
                    
                    full_pr_body = (
                        f"### 🤖 LogicFlow Restoration Summary\n"
                        f"{explanation}\n\n"
                        f"### 🛡️ Senior Peer Review\n"
                        f"{review_comments}\n\n"
                        f"### 🧪 Validation Status\n"
                        f"- Docker Sandbox: PASS"
                    )

                    # 5. PR CREATION
                    pr_url = create_pull_request(
                        issue_id=issue_id,
                        fixed_code=restored_code,
                        file_path=Config.DEMO_CODE_PATH,
                        explanation=full_pr_body
                    )

                return {
                    "success": success,
                    "restored_code": restored_code,
                    "explanation": explanation,
                    "review": review_comments,
                    "test_log": test_log,
                    "pr_url": pr_url,
                    "model_used": self.model
                }
        except Exception as e:
            logger.warning(f"{self.model} failed: {e}")

        return {"success": False, "test_log": "All restoration attempts failed."}

# --- Initialization for Streamlit ---
if 'archeologist' not in st.session_state:
    st.session_state.archeologist = DigitalArcheologist()

archeologist = st.session_state.archeologist