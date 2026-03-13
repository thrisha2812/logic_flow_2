import streamlit as st
import os
import sys

sys.path.append(os.getcwd())

from agents.core import DigitalArcheologist
from tools.demo_utils import generate_broken_code
from tools.faiss_tool import ingest_code
from tools.docker_test_tool import run_isolated_test
from config import Config
from tools.github_tool import create_github_issue, get_github_issues, post_github_comment

# 1. Page Config
st.set_page_config(page_title="LogicFlow AI", layout="wide")

# 2. State & Logs
if "logs" not in st.session_state:
    st.session_state.logs = "System Initialized: LogicFlow Online."
if 'archeologist' not in st.session_state:
    st.session_state.archeologist = DigitalArcheologist()

def add_log(message):
    st.session_state.logs += f"\n[INFRA]: {message}"

# 3. Sidebar
st.sidebar.title("Infrastructure Status")
if st.sidebar.button("Reset Excavation Site"):
    generate_broken_code()
    ingest_code()
    st.rerun()

issues = get_github_issues()

# 4. Main UI
st.title("LogicFlow: Autonomous Bug Repair")
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Target Repository")
    try:
        with open("demo/broken_code.py", "r") as f:
            code = f.read()
        st.code(code, language="python")
    except: st.warning("File not found.")

with col2:
    st.header("Agent Activity")
    log_area = st.empty()
    log_area.code(st.session_state.logs, language="bash")

    if st.button("Start AI Repair"):
        add_log("Archeologist descending into codebase...")
        log_area.code(st.session_state.logs, language="bash")
        
        new_id = create_github_issue("Discovery: Corrupted Artifact", "Analyzing demo/broken_code.py")
        
        if new_id:
            add_log(f"Issue #{new_id} logged.")
            result = st.session_state.archeologist.excavate_and_repair(new_id, code)
            
            if result.get("success"):
          
                st.success(f" Repair Successful! PR: {result.get('pr_url')}")
                
                with st.expander("🔍 View LogicFlow's Reasoning & Review", expanded=True):
                    st.subheader("AI Explanation")
                    st.info(result.get('explanation', "No explanation provided."))
                    
                    st.subheader("🛡️ Senior Peer Review")
                    # We use .get('review') which we added to the core.py return dictionary
                    st.success(result.get('review', "Review not available."))
                    
                    st.subheader("Docker Sandbox Verification")
                    st.code(result.get('test_log'), language="bash")
                    
                    if result.get('pr_url'):
                        st.link_button("View Pull Request on GitHub", result['pr_url'])
            else:
                st.error("Stabilization failed.")
                add_log(f"Error: {result.get('test_log')}")
            
            log_area.code(st.session_state.logs, language="bash")

st.caption("Built by Dimply and Thrisha | Sahyadri College of Engineering")