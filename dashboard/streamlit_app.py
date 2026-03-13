import streamlit as st
import os
import sys
from demo.broken_code import generate_broken_code

# Ensure the root directory is in the path for tool imports
sys.path.append(os.getcwd())
from tools.demo_utils import generate_broken_code
from tools.faiss_tool import ingest_code
from tools.docker_test_tool import run_isolated_test
from config import Config
from tools.github_tool import create_github_issue, get_github_issues, post_github_comment

def report_progress(issue_id, message):
    """The one-stop function for the Agent to talk to the world"""
    add_log(message)  # Updates your Dashboard
    post_github_comment(issue_id, f"🤖 [LogicFlow]: {message}") # Updates GitHub

# 1. Page Configuration
st.set_page_config(page_title="LogicFlow AI", layout="wide")

# 2. Initialize Session State for Infrastructure Logs
if "logs" not in st.session_state:
    st.session_state.logs = "System Initialized: LogicFlow Infrastructure Online."

def add_log(message):
    """Helper to update the live terminal log"""
    st.session_state.logs += f"\n[INFRA]: {message}"
if "indexed" not in st.session_state:
    # This runs only once when the app starts
    with st.spinner("Initial indexing of excavation site..."):
        ingest_code()
        st.session_state.indexed = True
        # Note: We can't update log_area yet because it hasn't been created
        # So we just add to the session state string
        add_log("Codebase indexed and ready for retrieval.")
# 3. Sidebar: Infrastructure Health & Issues
st.sidebar.title("Infrastructure Status")

# Sidebar Health Check
with st.sidebar.expander("System Health", expanded=True):
    if Config.GITHUB_TOKEN:
        st.write("GitHub Auth: Verified")
    else:
        st.error("GitHub Auth: Missing")
    st.write(f"Repo: {Config.GITHUB_REPO}")

st.sidebar.markdown("---")
if st.sidebar.button("Reset Excavation Site (New Bug)"):
    bug_type = generate_broken_code()
    add_log(f"Injected new artifact: {bug_type}")
    st.sidebar.success(f"Injected: {bug_type}")
    st.rerun() # Refresh the UI to show the new code in Col1
st.sidebar.subheader("Open Issues")
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

if st.sidebar.button("Clear Logs"):
    st.session_state.logs = "System Initialized: LogicFlow Infrastructure Online."
    st.rerun()

# 4. Main UI Header
st.title("LogicFlow: Autonomous Bug Repair")
st.markdown("---")

col1, col2 = st.columns([1, 1])

# Column 1: Source Code View
with col1:
    st.header("Target Repository")
    st.info(f"Active Site: {Config.GITHUB_REPO}")
    
    try:
        with open("demo/broken_code.py", "r") as f:
            code = f.read()
        st.subheader("Source Code (demo/broken_code.py)")
        st.code(code, language="python")
    except FileNotFoundError:
        st.warning("Source file demo/broken_code.py not found.")

# Column 2: Infrastructure & Agent Activity Logs
with col2:
    st.header("Agent Activity")
    
    # Live scrolling log area
    log_area = st.empty()
    log_area.code(st.session_state.logs, language="bash")

    st.markdown("---")
    
    # Action area for triggering infrastructure tasks
    action_container = st.container()
    
    if st.button("Start AI Repair"):
        with action_container:
            add_log("Initializing repair process...")
            log_area.code(st.session_state.logs, language="bash")
            
            # 1. Create a new issue
            new_id = create_github_issue(
                "Detected Bug in Source", 
                "Infrastructure trigger: Identifying failure in demo/broken_code.py"
            )
            
            if new_id and str(new_id).isdigit():
                add_log(f"GitHub Issue #{new_id} created successfully.")
                log_area.code(st.session_state.logs, language="bash")
                
                # 2. Post the comment
                add_log("Posting status update to GitHub...")
                comment_result = post_github_comment(
                    new_id, 
                    "LogicFlow Agent is analyzing the codebase via FAISS."
                )
                
                if "success" in str(comment_result).lower():
                    add_log("GitHub synchronization complete.")
                    st.success(f"Pipeline executed for Issue {new_id}")
                else:
                    add_log("Warning: GitHub comment failed.")
                
                log_area.code(st.session_state.logs, language="bash")
            else:
                add_log("Error: Could not create GitHub issue.")
                st.error("Infrastructure failure. Check logs.")

# 5. Footer / Repository Overview
st.markdown("---")
st.header("Active Repository Issues")
if isinstance(issues, list) and len(issues) > 0:
    for issue in issues:
        st.text(f"Issue #{issue['number']}: {issue['title']}")
else:
    st.info("No active issues detected in the remote repository.")

st.markdown("---")
st.caption("Built by Dimply and Thrisha | Sahyadri College of Engineering")