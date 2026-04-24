import os
os.environ["STREAMLIT_SERVER_WATCHER_TYPE"] = "none"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import logging
logging.getLogger("transformers").setLevel(logging.ERROR)

import sys
import streamlit as st

sys.path.append(os.getcwd())

from agents.core import DigitalArcheologist
from tools.demo_utils import generate_broken_code
from tools.faiss_tool import ingest_code
from config import Config
from tools.github_tool import get_github_issues, post_github_comment

st.set_page_config(page_title="LogicFlow AI", layout="wide")

if "logs" not in st.session_state:
    st.session_state.logs = "System Initialized: LogicFlow Online."
if "archeologist" not in st.session_state:
    st.session_state.archeologist = DigitalArcheologist()


def add_log(message):
    st.session_state.logs += f"\n[INFRA]: {message}"


st.sidebar.title("Infrastructure Status")

if st.sidebar.button("Reset Excavation Site (New Bug)"):
    bug_type = generate_broken_code()
    with st.spinner("Re-indexing new artifact..."):
        ingest_code()
    add_log(f"Injected new artifact: {bug_type}")
    st.rerun()

issues = get_github_issues()

st.sidebar.markdown("---")
st.sidebar.subheader("Select Issue to Solve")

selected_issue_data = None
if isinstance(issues, list) and len(issues) > 0:
    issue_options = {f"#{i['number']}: {i['title']}": i for i in issues}
    selection = st.sidebar.selectbox("Active GitHub Issues", options=list(issue_options.keys()))
    selected_issue_data = issue_options[selection]
else:
    st.sidebar.info("No open issues found.")

st.title("LogicFlow: Autonomous Bug Repair")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("Target Repository")
    st.info(f"Active Site: {Config.GITHUB_REPO}")

    try:
        with open("demo/broken_code.py", "r", encoding="utf-8") as f:
            code = f.read()
        st.subheader("Source Code (demo/broken_code.py)")
        st.code(code, language="python")
    except FileNotFoundError:
        code = ""
        st.warning("Source file not found.")

with col2:
    st.header("Agent Activity")

    log_area = st.empty()
    log_area.code(st.session_state.logs, language="bash")

    st.markdown("---")

    if selected_issue_data:
        issue_num = selected_issue_data["number"]
        issue_body = selected_issue_data.get("body", "No description provided.")

        st.write(f"**Targeting Issue:** #{issue_num}")
        st.caption(f"Description: {issue_body[:100]}...")

        if st.button(f"Solve Issue #{issue_num}"):
            add_log(f"Archeologist analyzing GitHub Issue #{issue_num}...")
            log_area.code(st.session_state.logs, language="bash")

            with st.spinner("LogicFlow is investigating and repairing..."):
                result = st.session_state.archeologist.excavate_and_repair(
                    issue_id=issue_num,
                    broken_code=code,
                    github_issue_text=issue_body,
                )

                if result.get("success"):
                    st.balloons()
                    st.success(f"Repair Successful! PR: {result.get('pr_url')}")

                    with st.expander("View LogicFlow reasoning and review", expanded=True):
                        st.subheader("AI Explanation")
                        st.info(result.get("explanation", "No explanation provided."))

                        st.subheader("Senior Peer Review")
                        st.success(result.get("review", "Review not available."))

                        st.subheader("Docker Sandbox Verification")
                        st.code(result.get("test_log"), language="bash")

                        if result.get("pr_url"):
                            st.link_button("View Pull Request on GitHub", result["pr_url"])

                    fix_msg = (
                        "Artifact Repaired Successfully!\n\n"
                        f"AI Reasoning: {result.get('explanation')}\n\n"
                        f"Fixed Code:\n```python\n{result['restored_code']}\n```"
                    )
                    post_github_comment(issue_num, fix_msg)
                    add_log("Fix verified and pushed to GitHub.")
                else:
                    st.error("Stabilization failed.")
                    add_log(f"Error: {result.get('test_log')}")

                log_area.code(st.session_state.logs, language="bash")
    else:
        st.warning("Please select an issue from the sidebar to begin repair.")

st.markdown("---")
