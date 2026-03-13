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

# 1. Page Configuration
st.set_page_config(page_title="LogicFlow AI", layout="wide")

# 2. State & Logs
if "logs" not in st.session_state:
    st.session_state.logs = "System Initialized: LogicFlow Online."
if 'archeologist' not in st.session_state:
    st.session_state.archeologist = DigitalArcheologist()

def add_log(message):
    st.session_state.logs += f"\n[INFRA]: {message}"

# 3. Sidebar: Infrastructure Health & Issues
st.sidebar.title("Infrastructure Status")

# Bug Generator Button
if st.sidebar.button("Reset Excavation Site (New Bug)"):
    bug_type = generate_broken_code()
    with st.spinner("Re-indexing new artifact..."):
        ingest_code()
    add_log(f"Injected new artifact: {bug_type}")
    st.rerun()

# Fetch active issues for the dropdown
issues = get_github_issues()

st.sidebar.markdown("---")
st.sidebar.subheader("Select Issue to Solve")

selected_issue_data = None
if isinstance(issues, list) and len(issues) > 0:
    # Create a dictionary for easy lookup
    issue_options = {f"#{i['number']}: {i['title']}": i for i in issues}
    selection = st.sidebar.selectbox("Active GitHub Issues", options=list(issue_options.keys()))
    selected_issue_data = issue_options[selection]
else:
    st.sidebar.info("No open issues found.")

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
        st.warning("Source file not found.")

# Column 2: Agent Activity & Repair Logic
with col2:
    st.header("Agent Activity")
    
    log_area = st.empty()
    log_area.code(st.session_state.logs, language="bash")

    st.markdown("---")
    
    # Check if an issue is selected
    if selected_issue_data:
        issue_num = selected_issue_data['number']
        issue_body = selected_issue_data.get('body', 'No description provided.')
        
        st.write(f"**Targeting Issue:** #{issue_num}")
        st.caption(f"Description: {issue_body[:100]}...")

        if st.button(f"🚀 Solve Issue #{issue_num}"):
            add_log(f"Archeologist analyzing GitHub Issue #{issue_num}...")
            log_area.code(st.session_state.logs, language="bash")
            
            with st.spinner("LogicFlow is investigating and repairing..."):
                # Pass the real GitHub issue text to the brain
                result = st.session_state.archeologist.excavate_and_repair(
                    issue_id=issue_num, 
                    broken_code=code, 
                    github_issue_text=issue_body
                )
                
                if result.get("success"):
                    st.balloons()
                    st.success(f"Repair Successful! PR: {result.get('pr_url')}")
                    
                    with st.expander("🔍 View LogicFlow's Reasoning & Review", expanded=True):
                        st.subheader("AI Explanation")
                        st.info(result.get('explanation', "No explanation provided."))
                        
                        st.subheader("🛡️ Senior Peer Review")
                        st.success(result.get('review', "Review not available."))
                        
                        st.subheader("Docker Sandbox Verification")
                        st.code(result.get('test_log'), language="bash")
                        
                        if result.get('pr_url'):
                            st.link_button("View Pull Request on GitHub", result['pr_url'])

                    # Post the final fix comment
                    fix_msg = f"Artifact Repaired Successfully!\n\n**AI Reasoning:** {result.get('explanation')}\n\nFixed Code:\n```python\n{result['restored_code']}\n```"
                    post_github_comment(issue_num, fix_msg)
                    add_log("Fix verified and pushed to GitHub.")
                else:
                    st.error("Stabilization failed.")
                    add_log(f"Error: {result.get('test_log')}")
                
                log_area.code(st.session_state.logs, language="bash")
    else:
        st.warning("Please select an issue from the sidebar to begin repair.")

st.markdown("---")
st.caption("Built by Dimply and Thrisha | Sahyadri College of Engineering")