import random

def generate_broken_code():
    """This function is safe here. It writes TO the other file."""
    scenarios = [
        {"name": "Zero Division", "code": "def run():\n    return 10 / 0\nrun()"},
        {"name": "Index Error", "code": "def run():\n    items = [1]\n    return items[5]\nrun()"}
    ]
    bug = random.choice(scenarios)
    
    # We open the OTHER file and overwrite it
    with open("demo/broken_code.py", "w") as f:
        f.write(bug["code"])
    
    return bug["name"]