import subprocess
import os

def run_isolated_test(code_to_test):
    """
    Takes a string of Python code, saves it to a file, 
    and runs it inside a Docker container.
    """
    # 1. Ensure the demo folder exists and save the code
    os.makedirs("demo", exist_ok=True)
    test_file_path = "demo/test_run.py"
    
    with open(test_file_path, "w") as f:
        f.write(code_to_test)
    
    print(f"🚀 Running test in Docker...")

    # 2. Docker Command:
    # -v mounts your local 'demo' folder to '/app' in the container
    # It runs the file and then deletes the container (--rm)
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{os.getcwd()}/demo:/app",
        "python:3.10-slim", "python", "/app/test_run.py"
    ]

    try:
        # Run the command and capture the output
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return True, f"Success: {result.stdout}"
        else:
            return False, f"Error: {result.stderr}"
            
    except Exception as e:
        return False, f"Docker Execution Failed: {str(e)}"