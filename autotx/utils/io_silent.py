from typing import Any
from autogen.io import IOConsole

class IOSilent(IOConsole): # type: ignore
    """A console input/output stream."""

    def print(self, *objects: Any, sep: str = " ", end: str = "\n", flush: bool = False) -> None:
        pass
    # Pass all args to the base class
    def input(self, prompt: str = "", *, password: bool = False) -> str:
        return super().input(prompt, password=password) # type: ignore
