import streamlit as st
import os
import sys

# Ensure the root directory is in the path for tool imports
sys.path.append(os.getcwd())

from tools.faiss_tool import ingest_code
from tools.docker_test_tool import run_isolated_test
from config import Config
from tools.github_tool import create_github_issue, get_github_issues, post_github_comment

st.set_page_config(page_title="LogicFlow AI", layout="wide")

# --- Sidebar: System Status ---
st.sidebar.title("Infrastructure Status")
st.sidebar.subheader("Open Issues")

# Fetch issues once at the start to use in both Sidebar and Main UI
issues = get_github_issues()

if isinstance(issues, list) and len(issues) > 0:
    for issue in issues:
        st.sidebar.write(f"ID {issue['number']}: {issue['title']}")
elif isinstance(issues, str):
    st.sidebar.error(issues)
else:
    st.sidebar.info("No open issues found")

st.sidebar.markdown("---")
if st.sidebar.button("Check Docker Lab"):
    success, result = run_isolated_test("print('Docker Online')")
    if success:
        st.sidebar.success("Docker: ONLINE")
    else:
        st.sidebar.error("Docker: OFFLINE")

if st.sidebar.button("Re-Index Codebase"):
    with st.spinner("Indexing..."):
        ingest_code()
        st.sidebar.success("FAISS Index Updated")

# --- Main UI ---
st.title("LogicFlow: Autonomous Bug Repair")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("Target Repository")
    st.info(f"Working on: {Config.GITHUB_REPO}")
    
    try:
        with open("demo/broken_code.py", "r") as f:
            code = f.read()
        st.subheader("Source Code (demo/broken_code.py)")
        st.code(code, language="python")
    except FileNotFoundError:
        st.warning("demo/broken_code.py not found")

with col2:
    st.header("Agent Activity")
    log_placeholder = st.empty()
    log_placeholder.text_area("Live Logs", value="Waiting for agent to start...", height=300)

    # --- THE REPAIR BUTTON ---
    # Placed inside Column 2 so it is clearly part of the Agent's action area
    action_log = st.container()
    
    if st.button("Start AI Repair"):
        with action_log:
            st.write("Initializing repair process...")
            
            # 1. Create a new issue
            new_id = create_github_issue(
                "Detected Bug in Source", 
                "The agent has identified a potential failure in demo/broken_code.py"
            )
            
            if isinstance(new_id, int):
                st.write(f"Created GitHub Issue Number: {new_id}")
                
                # 2. Post the comment
                st.write("Communicating with GitHub API...")
                comment_result = post_github_comment(
                    new_id, 
                    "LogicFlow Agent has started work on this issue."
                )
                
                if "success" in str(comment_result).lower():
                    st.success(f"Status updated on Issue {new_id}")
                else:
                    st.error("Failed to post status update to GitHub")
                
                # Integration Hook for Dimply:
                # result = agent.run_logic(new_id)
            else:
                st.error("Could not initialize GitHub Issue. Check your Token permissions.")

# --- Bottom Section: Issue List ---
st.markdown("---")
st.header("Active Repository Issues")
if isinstance(issues, list) and len(issues) > 0:
    for issue in issues:
        st.text(f"Issue #{issue['number']}: {issue['title']}")
else:
    st.info("No active issues detected. Ensure GITHUB_REPO is correct in config.py.")

st.markdown("---")
st.caption("Built by Dimply and Thrisha | Sahyadri College of Engineering")