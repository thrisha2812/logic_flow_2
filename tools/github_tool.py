import requests
from config import Config

def get_github_issues():
    url = f"https://api.github.com/repos/{Config.GITHUB_REPO}/issues?state=open"
    headers = {
        "Authorization": f"token {Config.GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            issues_data = response.json()
            if not issues_data:
                return []
            # Returns a list of dicts for better UI handling
            return [{"number": i["number"], "title": i["title"]} for i in issues_data]
        else:
            return f"GitHub Error: {response.status_code}"
    except Exception as e:
        return f"Connection Error: {str(e)}"
    # Keep this for Dimply's Agent, but we'll use the function above for the Dashboard
def get_github_tools():
    # We will fix the agent's toolkit later if Dimply needs it, 
    # but for your dashboard, use get_github_issues()
    return []
def create_github_issue(title, body):
    """Creates a new issue in the repository."""
    url = f"https://api.github.com/repos/{Config.GITHUB_REPO}/issues"
    
    headers = {
        "Authorization": f"token {Config.GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {"title": title, "body": body}
    
   
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
            issue_data = response.json()
            return issue_data['number']  # Return the actual integer (e.g., 5)
    return None
    
def post_github_comment(issue_number, comment_body):
    """Posts a comment to a specific GitHub issue."""
    url = f"https://api.github.com/repos/{Config.GITHUB_REPO}/issues/{issue_number}/comments"
    
    headers = {
        "Authorization": f"token {Config.GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {"body": comment_body}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            return "✅ Comment posted successfully!"
        else:
            return f"❌ Failed to post comment: {response.status_code}"
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"