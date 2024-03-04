import subprocess


def main():
    subprocess.run(["docker", "build", "-t", "development_node", "."], check=True)
    subprocess.run(
        ["docker", "run", "-p", "8545:8545", "--env-file", ".env", "development_node"],
        check=True,
    )


if __name__ == "__main__":
    main()
