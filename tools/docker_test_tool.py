import docker
import logging
import tempfile
import os

logger = logging.getLogger("LogicFlow.Docker")

def run_isolated_test(code_snippet):
    client = docker.from_env()
    container = None
    try:
        logger.info("Connecting to Docker Engine...")
        
        # 1. Create a truly isolated environment (but allow network for pip install)
        container = client.containers.run(
            image="python:3.12-slim",
            command="sleep 30", # Container stays alive for 30s
            detach=True,
            remove=True,
            network_disabled=False, # We need network to install flake8
            mem_limit="128m"
        )

        logger.info("Writing artifact to sandbox and verifying...")
        
        import base64
        # Encode to avoid escaping issues in shell
        encoded_code = base64.b64encode(code_snippet.encode('utf-8')).decode('utf-8')
        
        # Setup: decode file, install flake8
        setup_cmd = f"echo {encoded_code} | base64 -d > artifact.py && pip install flake8 > /dev/null 2>&1"
        container.exec_run(cmd=['sh', '-c', setup_cmd], workdir="/")
        
        # Run Static Analysis (Flake8) to catch complex errors
        lint_log = container.exec_run(cmd=['flake8', 'artifact.py'], workdir="/")
        lint_output = lint_log.output.decode("utf-8").strip()
        
        # Execute the script
        exec_log = container.exec_run(cmd=['python', 'artifact.py'], workdir="/")
        exec_output = exec_log.output.decode("utf-8").strip()
        
        exit_code = exec_log.exit_code
        
        # Format logs
        logs = ""
        if lint_output:
            logs += f"--- Static Analysis (Flake8) ---\n{lint_output}\n"
        logs += f"--- Execution Output ---\n{exec_output}"
        
        # 3. Cleanup
        container.stop()
        
        # Success requires both the code executing and no linting errors
        success = (exit_code == 0) and (lint_log.exit_code == 0)
        logger.info(f"Sandbox verification complete. Success: {success}")
        return success, logs

    except Exception as e:
        logger.error(f"Docker Sandbox Failure: {e}")
        if container:
            try: container.kill()
            except: pass
        return False, f"Sandbox Error: {e}"