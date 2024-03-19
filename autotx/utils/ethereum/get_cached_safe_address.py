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
