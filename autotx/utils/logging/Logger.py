import os
import io
import sys
from typing import TextIO
from autogen import runtime_logging
from autogen.io import IOStream, IOConsole
from autotx.utils.logging.IOSilent import IOSilent
from autotx.utils.logging.TeeStream import TeeStream


class Logger:
    dir: str | None
    original_stdout: TextIO
    original_stderr: TextIO
    captured_stdout: io.StringIO
    captured_stderr: io.StringIO
    tee_stdout: TeeStream
    tee_stderr: TeeStream

    def __init__(
        self,
        dir: str | None = None,
        silent: bool = False
    ):
        self.dir = dir

        if dir:
            # Check if directory exists, throw error if it does
            if os.path.exists(dir):
                raise FileExistsError(f"The directory '{dir}' already exists.")
            # Make the directory
            os.makedirs(dir, exist_ok=True)

        if silent:
            IOStream.set_global_default(IOSilent())
        else:
            IOStream.set_global_default(IOConsole())

    def start(self) -> None:
        if not self.dir:
            return

        # Initialize StringIO buffers for capturing stdout and stderr
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.captured_stdout = io.StringIO()
        self.captured_stderr = io.StringIO()
        self.tee_stdout = TeeStream(self.original_stdout, self.captured_stdout)
        self.tee_stderr = TeeStream(self.original_stderr, self.captured_stderr)

        # Redirect stdout and stderr
        sys.stdout = self.tee_stdout
        sys.stderr = self.tee_stderr

        # Start collecting stdout & stderr
        runtime_logging.start(config={
            "dbname": os.path.join(self.dir, "agent.db")
        })

    def stop(self) -> None:
        if not self.dir:
            return

        # Restore original stdout and stderr
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

        # Write captured stdout and stderr to files
        with open(os.path.join(self.dir, "stdout.txt"), "w") as f:
            f.write(self.captured_stdout.getvalue())
        with open(os.path.join(self.dir, "stderr.txt"), "w") as f:
            f.write(self.captured_stderr.getvalue())

        # Stop runtime logging
        runtime_logging.stop()
