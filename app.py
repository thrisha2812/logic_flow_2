from tools.faiss_tool import retrieve_context, ingest_code
from tools.docker_test_tool import run_isolated_test
from tools.github_tool import get_github_tools
from config import Config

def main():
    print("--- LogicFlow Infrastructure Check ---")
    
    # 1. Check GitHub
    if not Config.GITHUB_TOKEN:
        print("[FAIL] Error: GITHUB_TOKEN not found in Config. Check your .env file.")
        return
    try:
        tools = get_github_tools()
        print(f"[OK] GitHub Tools Loaded: {len(tools)} tools available")
    except Exception as e:
        print(f"[FAIL] GitHub Error: {e}")

    # 2. Check FAISS
    try:
        ingest_code() # Initialize the index first
        results = retrieve_context("test query")
        print(f"[OK] FAISS Retrieval working. Found {len(results)} snippets.")
    except Exception as e:
        print(f"[FAIL] FAISS Error: {e}")

    # 3. Check Docker
    try:
        success, output = run_isolated_test("print('Infrastructure Ready')\n")
        if success:
            print(f"[OK] Docker Lab is LIVE: {output.strip()}")
        else:
            print(f"[FAIL] Docker Lab Error: {output}")
    except Exception as e:
        print(f"[FAIL] Docker connection failed: {e}")

if __name__ == "__main__":
    main()