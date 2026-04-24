import logging
import json
import requests
import streamlit as st
from config import Config
from tools.faiss_tool import retrieve_context
from tools.docker_test_tool import run_isolated_test
from tools.github_tool import create_pull_request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LogicFlow")


class DigitalArcheologist:
    MAX_REPAIR_ATTEMPTS = 2
    REPAIR_TIMEOUT_SECONDS = Config.OLLAMA_TIMEOUT

    def __init__(self):
        """Initializes the LogicFlow AI with access to local Ollama models."""
        try:
            self.base_url = Config.OLLAMA_BASE_URL
            self.model = Config.OLLAMA_MODEL
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            logger.info(f"LogicFlow Pipeline Architect active. Connected to Ollama at {self.base_url}")
        except Exception as e:
            logger.error(f"Initialization failure (Ollama not reachable): {e}")

    def review_restoration(self, code, explanation):
        review_prompt = f"""
        Review this proposed Python fix for security, efficiency, and PEP8 standards.
        PROPOSED CODE:
        {code}

        AI EXPLANATION:
        {explanation}

        Provide a critical review in 3 bullets max. If there are no issues, start with 'LGTM'.
        """

        try:
            logger.info(f"Attempting Senior Peer Review with {self.model}...")
            payload = {
                "model": self.model,
                "prompt": review_prompt,
                "stream": False,
                "options": {
                    "temperature": Config.LLM_TEMPERATURE,
                    "num_predict": 220,
                },
            }
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=45)
            response.raise_for_status()
            return response.json().get("response", "Review unavailable.")
        except Exception as e:
            return f"Review system failed: {e}"

    def _normalize_text(self, value, fallback=""):
        if isinstance(value, str):
            return value.strip()
        if value is None:
            return fallback
        if isinstance(value, (int, float, bool)):
            return str(value)
        return fallback

    def _request_repair(self, prompt):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": Config.LLM_TEMPERATURE,
                "num_predict": Config.LLM_MAX_TOKENS,
            },
        }
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=self.REPAIR_TIMEOUT_SECONDS,
        )
        response.raise_for_status()

        response_data = response.json()
        raw_response = response_data.get("response", "{}")
        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError:
            logger.warning("Model returned invalid JSON. Raw response: %s", raw_response)
            return {}

        if not isinstance(parsed, dict):
            logger.warning("Model returned non-object JSON. Parsed value: %r", parsed)
            return {}

        return parsed

    def _trim(self, text, max_chars):
        normalized = self._normalize_text(text, "")
        if len(normalized) <= max_chars:
            return normalized
        return normalized[:max_chars] + "\n... [truncated]"

    def _build_initial_prompt(self, issue_id, github_issue_text, context_str, broken_code):
        return f"""
        Fix the Python artifact for GitHub issue #{issue_id}.

        Issue:
        {github_issue_text if github_issue_text else 'Generic bug repair.'}

        Context:
        {self._trim(context_str, Config.MAX_CONTEXT_CHARS)}

        Broken code:
        {self._trim(broken_code, Config.MAX_BROKEN_CODE_CHARS)}

        Return strict JSON only:
        {{"code": "<python code>", "explanation": "<one short sentence>"}}

        Rules:
        - code must be a string
        - explanation must be a string
        - produce runnable Python
        - do not leave division by zero, undefined names, or placeholders
        - keep explanation concise
        """

    def _build_retry_prompt(self, issue_id, github_issue_text, context_str, broken_code, previous_code, test_log):
        return f"""
        Retry the Python repair for GitHub issue #{issue_id}.

        Issue:
        {github_issue_text if github_issue_text else 'Generic bug repair.'}

        Context:
        {self._trim(context_str, Config.MAX_CONTEXT_CHARS)}

        Broken code:
        {self._trim(broken_code, Config.MAX_BROKEN_CODE_CHARS)}

        Previous attempt:
        {self._trim(previous_code, Config.MAX_BROKEN_CODE_CHARS)}

        Failure details:
        {self._trim(test_log, 1200)}

        Return strict JSON only:
        {{"code": "<python code>", "explanation": "<one short sentence>"}}

        Rules:
        - fix the runtime failure from Failure details
        - code must be a string
        - explanation must be a string
        - produce runnable Python
        - keep explanation concise
        """

    def excavate_and_repair(self, issue_id, broken_code, github_issue_text=None):
        search_query = github_issue_text if github_issue_text else broken_code[:100]
        context_snippets = retrieve_context(search_query)
        context_str = "\n---\n".join([str(snippet) for snippet in context_snippets])

        try:
            restored_code = ""
            explanation = "No explanation provided."
            success = False
            test_log = "No sandbox run performed."

            for attempt in range(1, self.MAX_REPAIR_ATTEMPTS + 1):
                if attempt == 1:
                    prompt = self._build_initial_prompt(issue_id, github_issue_text, context_str, broken_code)
                else:
                    prompt = self._build_retry_prompt(
                        issue_id,
                        github_issue_text,
                        context_str,
                        broken_code,
                        restored_code,
                        test_log,
                    )

                logger.info(f"Querying Oracle: {self.model} (attempt {attempt}/{self.MAX_REPAIR_ATTEMPTS})...")
                ai_data = self._request_repair(prompt)
                restored_code = self._normalize_text(ai_data.get("code", ""), "")
                explanation = self._normalize_text(
                    ai_data.get("explanation", "No explanation provided."),
                    "No explanation provided.",
                )

                if not restored_code:
                    test_log = "Model returned empty or invalid code JSON."
                    logger.warning("Repair attempt %s returned empty or invalid code.", attempt)
                    continue

                logger.info("Verifying restoration in Docker sandbox...")
                success, test_log = run_isolated_test(restored_code)

                if success:
                    break

                logger.warning("Repair attempt %s failed sandbox verification. Details:\n%s", attempt, test_log)

            pr_url = None
            review_comments = "No review performed."

            if success:
                review_comments = self.review_restoration(restored_code, explanation)
                full_pr_body = (
                    "### LogicFlow Restoration Summary\n"
                    f"{explanation}\n\n"
                    "### Senior Peer Review\n"
                    f"{review_comments}\n\n"
                    "### Validation Status\n"
                    "- Docker Sandbox: PASS"
                )

                pr_url = create_pull_request(
                    issue_id=issue_id,
                    fixed_code=restored_code,
                    file_path=Config.DEMO_CODE_PATH,
                    explanation=full_pr_body,
                )
            else:
                logger.error("All repair attempts failed sandbox verification. Details:\n%s", test_log)
                review_comments = "Skipped because all Docker sandbox verification attempts failed."

            return {
                "success": success,
                "restored_code": restored_code,
                "explanation": explanation,
                "review": review_comments,
                "test_log": test_log,
                "pr_url": pr_url,
                "model_used": self.model,
            }
        except Exception as e:
            logger.warning(f"{self.model} failed: {e}")

        return {"success": False, "test_log": "All restoration attempts failed."}


if "archeologist" not in st.session_state:
    st.session_state.archeologist = DigitalArcheologist()

archeologist = st.session_state.archeologist
