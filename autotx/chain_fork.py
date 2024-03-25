import subprocess
from autotx.utils.ethereum.cached_safe_address import delete_cached_safe_address

container_name = "autotx_chain_fork"

def start():
    delete_cached_safe_address()
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
