from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.utilities.github import GitHubAPIWrapper
from config import Config
import os

# Set environment variables so the wrapper can find them
os.environ["GITHUB_APP_AUTH_TYPE"] = "token"
os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"] = Config.GITHUB_TOKEN

def get_github_tools():
    """
    Returns the standard GitHub tools that Dimply's 
    manager agent will use to talk to the repo.
    """
    github = GitHubAPIWrapper(github_repository=Config.GITHUB_REPO)
    toolkit = GitHubToolkit.from_github_api_wrapper(github)
    return toolkit.get_tools()