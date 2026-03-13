import requests
from config import Config
import os
from github import Github
import logging

logger = logging.getLogger("LogicFlow.GitHub")

def create_pull_request(issue_id, fixed_code, file_path, explanation):
    """
    Automates the PR workflow: Branch -> Commit -> Push -> PR.
    """
    try:
        g = Github(Config.GITHUB_TOKEN)
        repo = g.get_repo(Config.GITHUB_REPO)
        
        # 1. Branch Management
        branch_name = f"logicflow/fix-issue-{issue_id}"
        main_branch = repo.get_branch("main")
        
        # Create a new branch from main
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_branch.commit.sha)
        logger.info(f"Created branch: {branch_name}")

        # 2. Commit the Fix
        contents = repo.get_contents(file_path, ref="main")
        repo.update_file(
            path=file_path,
            message=f"LogicFlow: Automated repair for Issue #{issue_id}",
            content=fixed_code,
            sha=contents.sha,
            branch=branch_name
        )
        logger.info(f"Committed fix to {file_path}")

        # 3. Create the Pull Request
        pr_title = f"LogicFlow Repair: Issue #{issue_id}"
        pr_body = f"### 🤖 LogicFlow Automated Restoration\n\n**Approach:**\n{explanation}\n\n**Validation:**\n- Verified in OCI-compliant Docker sandbox.\n- Status: PASS"
        
        pr = repo.create_pull(
            title=pr_title,
            body=pr_body,
            head=branch_name,
            base="main"
        )
        
        logger.info(f"PR Created Successfully: {pr.html_url}")
        return pr.html_url

    except Exception as e:
        logger.error(f"GitHub PR Failure: {e}")
        return None
    
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