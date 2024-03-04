from eth_account import Account

from sage_agent.utils.ethereum.cache import cache

def generate_agent_account() -> Account:
    result: str = cache(lambda: Account.create().key.hex(), "./.cache/agent.pk.txt")

    return Account.from_key(result)
