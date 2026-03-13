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
        
        # 1. Create a truly isolated environment
        # We use a simple 'cat' command to keep the container alive 
        # while we upload the script
        container = client.containers.run(
            image="python:3.12-slim",
            command="sleep 30", # Container stays alive for 30s
            detach=True,
            remove=True,
            network_disabled=True,
            mem_limit="128m"
        )

        logger.info("Executing artifact in sandbox...")
        
        # 2. Run the code directly via a 'Here Doc' to avoid Windows quote issues
        exec_log = container.exec_run(
            cmd=['python', '-c', code_snippet],
            workdir="/"
        )

        exit_code = exec_log.exit_code
        logs = exec_log.output.decode("utf-8")
        
        # 3. Cleanup
        container.stop()
        
        logger.info(f"Sandbox verification complete. Exit Code: {exit_code}")
        return (exit_code == 0), logs

    except Exception as e:
        logger.error(f"Docker Sandbox Failure: {e}")
        if container:
            try: container.kill()
            except: pass
        return False, f"Sandbox Error: {e}"