import os
from typing import Optional

class Cache:
    folder: str = None

    def __init__(self, folder: Optional[str] = ".cache"):
        self.folder = folder
        os.makedirs(folder, exist_ok=True)

    def read(self, file_name: str) -> str | None:
        try:
            with open(os.path.join(self.folder, file_name), "r") as file:
                return file.read().strip()  # Use strip() to remove newline characters
        except FileNotFoundError:
            print(file_name + " not found") 
            raise
        except Exception as e:
            print(f"An error occurred while reading {file_name}: {e}")
            raise

    def write(self, file_name: str, data: str):
        with open(os.path.join(self.folder, file_name), "w") as f:
            f.write(data)

    def remove(self, file_name: str):
        try:
            os.remove(os.path.join(self.folder, file_name))
        except FileNotFoundError:
            return
        except Exception as e:
            print(f"An error occurred while deleting {file_name}: {e}")
            raise

cache = Cache()
