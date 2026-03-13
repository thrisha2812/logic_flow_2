from tools.faiss_tool import retrieve_context
from tools.docker_test_tool import run_isolated_test
from tools.github_tool import get_github_tools
from config import Config

def main():
    print("--- LogicFlow Infrastructure Check ---")
    
    # 1. Check GitHub
    if not Config.GITHUB_TOKEN:
        print("❌ Error: GITHUB_TOKEN not found in Config. Check your .env file.")
        return
    try:
        tools = get_github_tools()
        print(f"✅ GitHub Tools Loaded: {len(tools)} tools available")
    except Exception as e:
        print(f"❌ GitHub Error: {e}")

    # 2. Check FAISS
    try:
        results = retrieve_context("test query")
        print(f"✅ FAISS Retrieval working. Found {len(results)} snippets.")
    except Exception as e:
        print(f"❌ FAISS Error: {e}")

    # 3. Check Docker
    try:
        success, output = run_isolated_test("print('Infrastructure Ready')")
        if success:
            print(f"✅ Docker Lab is LIVE: {output.strip()}")
        else:
            print(f"❌ Docker Lab Error: {output}")
    except Exception as e:
        print(f"❌ Docker connection failed: {e}")

if __name__ == "__main__":
    main()