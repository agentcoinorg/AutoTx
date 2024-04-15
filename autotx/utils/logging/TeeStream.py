from io import StringIO, TextIOWrapper
from typing import TextIO

class TeeStream(TextIOWrapper):
    original_stream: TextIO
    capture_buffer: StringIO

    def __init__(
        self,
        original_stream: TextIO,
        capture_buffer: StringIO
    ):
        super().__init__(original_stream.buffer)
        self.original_stream = original_stream
        self.capture_buffer = capture_buffer

    def write(self, message: str) -> int:
        self.capture_buffer.write(message)
        return self.original_stream.write(message)

    def flush(self) -> None:
        self.original_stream.flush()
        self.capture_buffer.flush()
