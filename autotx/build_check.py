import subprocess
import sys

def run() -> None:
    # Run mypy check
    result = subprocess.run(["mypy", "."], capture_output=True)
    print(result.stdout.decode())
    if result.returncode != 0:
        print("Type checking failed.")
        print(result.stderr.decode())
        sys.exit(1)