import os
from eth_account import Account
from autotx.utils.ethereum.cache import cache

def get_agent_account() -> Account | None:
    try:
        with open("./.cache/agent.pk.txt", "r") as f:
            return Account.from_key(f.read())
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"An error occurred while reading the agent account: {e}")
        raise
    
def create_agent_account() -> Account:
    result = cache(lambda: Account.create().key.hex(), "./.cache/agent.pk.txt")
    
    return Account.from_key(result)

def get_or_create_agent_account() -> Account:
    agent = get_agent_account()
    if agent:
        return agent
    return create_agent_account()

def delete_agent_account():
    try:
        os.remove("./.cache/agent.pk.txt")
    except FileNotFoundError:
        print("Agent account not found")
    except Exception as e:
        print(f"An error occurred while deleting the agent account: {e}")
        raise