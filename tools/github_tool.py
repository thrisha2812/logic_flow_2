import requests
from config import Config

def get_github_issues():
    """Fetches open issues directly from the GitHub API using your token."""
    # Convert 'user/repo' to the API URL format
    url = f"https://api.github.com/repos/{Config.GITHUB_REPO}/issues?state=open"
    print(f"DEBUG: Trying to reach {url}")
    headers = {
        "Authorization": f"token {Config.GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            issues = response.json()
            if not issues:
                return "No open issues found."
            # Format the issues into a simple string for the sidebar
            return "\n".join([f"#{i['number']}: {i['title']}" for i in issues])
        else:
            return f"❌ GitHub Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

# Keep this for Dimply's Agent, but we'll use the function above for the Dashboard
def get_github_tools():
    # We will fix the agent's toolkit later if Dimply needs it, 
    # but for your dashboard, use get_github_issues()
    return []