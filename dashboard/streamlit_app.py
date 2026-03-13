import streamlit as st
import os
import sys

# Ensure the root directory is in the path for tool imports
sys.path.append(os.getcwd())

from agents.core import DigitalArcheologist
from tools.demo_utils import generate_broken_code
from tools.faiss_tool import ingest_code
from tools.docker_test_tool import run_isolated_test
from config import Config
from tools.github_tool import create_github_issue, get_github_issues, post_github_comment

# Initialize the Brain
archeologist = DigitalArcheologist()

# 1. Page Configuration
st.set_page_config(page_title="LogicFlow AI", layout="wide")

# 2. Initialize Session State for Infrastructure Logs
if "logs" not in st.session_state:
    st.session_state.logs = "System Initialized: LogicFlow Infrastructure Online."

def add_log(message):
    """Helper to update the live terminal log"""
    st.session_state.logs += f"\n[INFRA]: {message}"

# Auto-Index on startup
if "indexed" not in st.session_state:
    with st.spinner("Initial indexing of excavation site..."):
        ingest_code()
        st.session_state.indexed = True
        add_log("Codebase indexed and ready for retrieval.")

# 3. Sidebar: Infrastructure Health & Issues
st.sidebar.title("Infrastructure Status")

with st.sidebar.expander("System Health", expanded=True):
    if Config.GITHUB_TOKEN:
        st.write("GitHub Auth: Verified")
    else:
        st.error("GitHub Auth: Missing")
    st.write(f"Repo: {Config.GITHUB_REPO}")

st.sidebar.markdown("---")

# Bug Generator Button
if st.sidebar.button("Reset Excavation Site (New Bug)"):
    bug_type = generate_broken_code()
    with st.spinner("Re-indexing new artifact..."):
        ingest_code() # Keep memory in sync with the new bug
    add_log(f"Injected new artifact: {bug_type}")
    st.sidebar.success(f"Injected: {bug_type}")
    st.rerun()

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
    
    log_area = st.empty()
    log_area.code(st.session_state.logs, language="bash")

    st.markdown("---")
    
    action_container = st.container()
    
    if st.button("Start AI Repair"):
        with action_container:
            add_log("Archeologist is descending into the codebase...")
            log_area.code(st.session_state.logs, language="bash")
            
            # --- PHASE 1: INITIALIZE ---
            new_id = create_github_issue(
                "Archeological Discovery: Corrupted Artifact", 
                "The agent is analyzing the strata of demo/broken_code.py"
            )
            
            if new_id and str(new_id).isdigit():
                add_log(f"Discovery logged as Issue #{new_id}")
                
                # --- PHASE 2: BRAIN WORK ---
                add_log("Consulting FAISS memory and Gemini Oracle...")
                log_area.code(st.session_state.logs, language="bash")
                
                # The Brain Logic
                result = archeologist.excavate_and_repair(new_id, code)
                
                # --- PHASE 3: REPORTING ---
                if result["success"]:
                    add_log("Stabilization Successful: Code passed Docker verification.")
                    # Post the fix to GitHub
                    fix_msg = f"Artifact Repaired Successfully!\n\nFixed Code:\n```python\n{result['restored_code']}\n```"
                    post_github_comment(new_id, fix_msg)
                    
                    # Accessing the model name from the 'meta' dictionary we defined in core.py
                    st.success(f"Restored by: {result.get('meta', {}).get('model', 'Gemini Oracle')}")
                    # Display the fix in the log
                    add_log("Syncing fix with remote repository...")
                else:
                    add_log(f"Restoration Failed: {result['test_log']}")
                    st.error("The agent could not stabilize the artifact.")
                
                log_area.code(st.session_state.logs, language="bash")
            else:
                st.error("Infrastructure failure: Could not connect to GitHub.")

# 5. Footer / Repository Overview
st.markdown("---")
st.header("Active Repository Issues")
if isinstance(issues, list) and len(issues) > 0:
    for issue in issues:
        st.text(f"Issue #{issue['number']}: {issue['title']}")
else:
    st.info("No active issues detected.")

st.markdown("---")
st.caption("Built by Dimply and Thrisha | Sahyadri College of Engineering")