import os

def get_env_vars() -> tuple[str, str, str, str, str]:
    rpc_url = os.getenv("RPC_URL")
    if not rpc_url:
        raise ValueError("RPC_URL is not set")

    user_pk = os.getenv("USER_PRIVATE_KEY")
    if not user_pk:
        raise ValueError("USER_PRIVATE_KEY is not set")

    return rpc_url, user_pk