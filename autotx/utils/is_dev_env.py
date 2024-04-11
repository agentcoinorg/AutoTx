import os

def is_dev_env() -> bool:
    return not os.getenv("SMART_ACCOUNT_ADDRESS")