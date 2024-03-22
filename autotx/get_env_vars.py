import os

def get_env_vars() -> tuple[str, str | None]:
    user_pk = os.getenv("USER_PRIVATE_KEY")
    if not user_pk:
        raise ValueError("USER_PRIVATE_KEY is not set")

    smart_account_addr = os.getenv("SMART_ACCOUNT_ADDRESS")

    return user_pk, smart_account_addr