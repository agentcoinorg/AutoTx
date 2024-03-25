import os

def get_cached_safe_address() -> str | None:
    try:
        with open("./.cache/safe.txt", "r") as file:
            return file.read().strip()  # Use strip() to remove newline characters
    except FileNotFoundError:
        print("Safe address not found")
        return None
    except Exception as e:
        print(f"An error occurred while reading ./.cache/safe.txt: {e}")
        raise

def save_cached_safe_address(safe_address: str):
    # Save the safe address in a file for future use
    with open("./.cache/safe.txt", "w") as f:
        f.write(safe_address)

def delete_cached_safe_address() -> bool:
    try:
        os.remove("./.cache/safe.txt")
        return True
    except FileNotFoundError:
        return False