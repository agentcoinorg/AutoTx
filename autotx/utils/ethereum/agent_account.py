import os
from eth_account import Account

from .cache import cache

def generate_agent_account() -> Account:
    result: str = cache(lambda: Account.create().key.hex(), "./.cache/agent.pk.txt")

    return Account.from_key(result)

def delete_agent_account():
    try:
        os.remove("./.cache/agent.pk.txt")
    except FileNotFoundError:
        print("Agent account not found")
    except Exception as e:
        print(f"An error occurred while deleting the agent account: {e}")
        raise