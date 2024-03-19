import os
from typing import Callable

def cache(func: Callable, file_name: str) -> str:
    try:
        with open(file_name, "r") as file:
            return file.read().strip()  # Use strip() to remove newline characters
    except FileNotFoundError:
        print(file_name + " not found, a new value will be generated.")
        # Extract the directory path from the file_name
        dir_name = os.path.dirname(file_name)
        # Create the directory if it does not exist
        if dir_name:  # Check if dir_name is not empty
            os.makedirs(dir_name, exist_ok=True)
    except Exception as e:
        print(f"An error occurred while reading " + file_name + ": {e}")
        raise
    result = func()

    with open(file_name, "w") as f:
        f.write(result)

    return result
