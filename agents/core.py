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

# Professional logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LogicFlow")

class DigitalArcheologist:
    def __init__(self):
        """Initializes the LogicFlow AI with access to Gemini 3 models."""
        try:
            self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
            # Primary: Flash (Speed/Cost), Secondary: Pro (Deep Review)
            self.available_models = ["gemini-3-flash-preview", "gemini-3.1-pro-preview"]
            logger.info("LogicFlow Pipeline Architect active.")
        except Exception as e:
            logger.error(f"Initialization failure: {e}")

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
            logger.info("Attempting Senior Peer Review with Gemini 3.1 Pro...")
            response = self.client.models.generate_content(
                model="gemini-3.1-pro-preview",
                contents=review_prompt
            )
            return response.text if response.text else "Review unavailable."
            
        except Exception as e:
            # FAILOVER: If Pro is busy/quota-limited, use Flash to ensure the pipeline doesn't stop
            if "429" in str(e) or "quota" in str(e).lower():
                logger.warning("Pro Quota reached. Falling back to Flash for Peer Review.")
                try:
                    response = self.client.models.generate_content(
                        model="gemini-3-flash-preview",
                        contents=review_prompt
                    )
                    return f"(Flash-Review): {response.text}"
                except:
                    return "Review system temporarily offline (Quota Limit)."
            return f"Reviewer failed: {e}"

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

        for model_name in self.available_models:
            try:
                logger.info(f"Querying Oracle: {model_name}...")
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                
                if response and response.text:
                    ai_data = json.loads(response.text)
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
                        "model_used": model_name
                    }
            except Exception as e:
                logger.warning(f"{model_name} failed: {e}")
                continue

        return {"success": False, "test_log": "All restoration attempts failed."}

# --- Initialization for Streamlit ---
if 'archeologist' not in st.session_state:
    st.session_state.archeologist = DigitalArcheologist()

archeologist = st.session_state.archeologist