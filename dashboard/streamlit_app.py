import streamlit as st
import os
import sys
sys.path.append(os.getcwd())
from tools.faiss_tool import ingest_code
from tools.docker_test_tool import run_isolated_test
from config import Config
from tools.github_tool import get_github_issues


st.set_page_config(page_title="LogicFlow AI", page_icon="", layout="wide")

# --- Sidebar: System Status ---
st.sidebar.title(" Infrastructure Status")
st.sidebar.subheader("Open Issues")
issues_text = get_github_issues() # Use the new function directly
st.sidebar.write(issues_text)

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
        st.sidebar.success("FAISS Index Updated!")

# --- Main UI ---
st.title(" LogicFlow: Autonomous Bug Repair")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.header(" Target Repository")
    st.info(f"Working on: **{Config.GITHUB_REPO}**")
    
    with open("demo/broken_code.py", "r") as f:
        code = f.read()
    st.subheader("Source Code (demo/broken_code.py)")
    st.code(code, language="python")

with col2:
    st.header(" Agent Activity")
    log_area = st.empty()
    log_area.text_area("Live Logs", value="Waiting for agent to start...", height=400)

    if st.button("Start AI Repair Loop", type="primary"):
        # This is where Dimply's code will eventually plug in
        st.warning("Connecting to Manager Agent...")
        # For now, we use a placeholder
        log_area.text_area("Live Logs", value="[System] Initializing Gemini Agent...\n[System] Searching FAISS for bug context...", height=400)

st.markdown("---")
st.caption("Built with ❤️ by Dimply & Thrisha | Sahyadri College of Engineering")