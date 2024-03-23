import os

def get_env_vars() -> str | None:
    smart_account_addr = os.getenv("SMART_ACCOUNT_ADDRESS")

    return smart_account_addr