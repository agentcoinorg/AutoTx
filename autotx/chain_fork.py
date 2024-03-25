import subprocess

from autotx.utils.ethereum import cache

container_name = "autotx_chain_fork"

def start():
    cache.remove("safe.txt")
    subprocess.run(["docker", "build", "-t", "autotx_chain_fork", "."], check=True)
    subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            container_name,
            "-p",
            "8545:8545",
            "--env-file",
            ".env",
            "autotx_chain_fork",
        ],
        check=True,
    )

def stop():
    subprocess.run(["docker", "container", "rm", container_name, "-f"], check=True)
