import subprocess

container_name = "development_node_container"


def start():
    subprocess.run(["docker", "build", "-t", "development_node", "."], check=True)
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
            "development_node",
        ],
        check=True,
    )


def stop():
    subprocess.run(["docker", "container", "rm", container_name, "-f"], check=True)
