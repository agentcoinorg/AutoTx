from autotx.utils.ethereum.cache import cache

SAFE_ADDRESS_FILE_NAME = "safe.txt"

def get_cached_safe_address() -> str | None:
    try:
        return cache.read(SAFE_ADDRESS_FILE_NAME)
    except Exception as e:
        return None

def save_cached_safe_address(safe_address: str):
    cache.write(SAFE_ADDRESS_FILE_NAME, safe_address)

def delete_cached_safe_address():
    cache.remove(SAFE_ADDRESS_FILE_NAME)
