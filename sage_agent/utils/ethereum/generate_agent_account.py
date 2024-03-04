from eth_account import Account

from .cache import cache

def generate_agent_account() -> Account:
    result: str = cache(lambda: Account.create().key.hex(), "./.cache/agent.pk.txt")

    return Account.from_key(result)
