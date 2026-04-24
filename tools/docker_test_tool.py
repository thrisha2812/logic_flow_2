import docker
import logging
import base64

logger = logging.getLogger("LogicFlow.Docker")


def _decode_output(result):
    output = getattr(result, "output", b"")
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace").strip()
    return str(output).strip()


def run_isolated_test(code_snippet):
    client = docker.from_env()
    container = None

    try:
        logger.info("Connecting to Docker Engine...")
        container = client.containers.run(
            image="python:3.12-slim",
            command="sleep 120",
            detach=True,
            remove=True,
            network_disabled=False,
            mem_limit="128m",
            working_dir="/workspace",
        )

        logger.info("Writing artifact to sandbox and verifying...")
        encoded_code = base64.b64encode(code_snippet.encode("utf-8")).decode("utf-8")
        setup_cmd = (
            "python - <<'PY'\n"
            "import base64\n"
            f"code = base64.b64decode('{encoded_code}').decode('utf-8')\n"
            "with open('/workspace/artifact.py', 'w', encoding='utf-8') as f:\n"
            "    f.write(code)\n"
            "PY\n"
            "pip install flake8 >/tmp/flake8-install.log 2>&1"
        )

        setup_result = container.exec_run(cmd=["sh", "-c", setup_cmd], workdir="/workspace")
        setup_output = _decode_output(setup_result)

        lint_result = container.exec_run(cmd=["flake8", "artifact.py"], workdir="/workspace")
        lint_output = _decode_output(lint_result)

        exec_result = container.exec_run(cmd=["python", "artifact.py"], workdir="/workspace")
        exec_output = _decode_output(exec_result)

        success = setup_result.exit_code == 0 and exec_result.exit_code == 0

        logs = [
            "Image: python:3.12-slim",
            f"Setup exit code: {setup_result.exit_code}",
            f"Lint exit code: {lint_result.exit_code}",
            f"Execution exit code: {exec_result.exit_code}",
        ]

        if lint_result.exit_code != 0:
            logs.append("Lint status: advisory only; runtime validation remains authoritative.")

        if setup_output:
            logs.append(f"--- Setup Output ---\n{setup_output}")
        if lint_output:
            logs.append(f"--- Static Analysis (Flake8) ---\n{lint_output}")
        if exec_output:
            logs.append(f"--- Execution Output ---\n{exec_output}")

        combined_logs = "\n".join(logs)

        logger.info(f"Sandbox verification complete. Success: {success}")
        logger.info("Docker verification details:\n%s", combined_logs)

        if container:
            container.stop()

        return success, combined_logs

    except Exception as e:
        logger.exception("Docker Sandbox Failure")
        if container:
            try:
                container.kill()
            except Exception:
                pass
        return False, f"Sandbox Error: {e}"
