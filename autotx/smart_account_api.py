import subprocess
import sys

container_name = "smart_account_api"

def start() -> None:
    build = subprocess.run(
        ["docker", "build", "-t", "smart_account_api", ".", "-f", "smart-account-api.Dockerfile"], capture_output=True
    )

    if build.returncode != 0:
        sys.exit(
            "Local node start up has failed. Make sure you have docker desktop installed and running"
        )

    subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            container_name,
            "-p",
            "7080:7080",
            "--env-file",
            ".env",
            "smart_account_api",
        ],
        check=True,
    )

def stop() -> None:
    subprocess.run(["docker", "container", "rm", container_name, "-f"], check=True)
