from typing import Optional, cast
from eth_account import Account
from eth_account.signers.local import LocalAccount
from autotx.utils.ethereum.cache import cache

AGENT_PK_FILE_NAME = "agent.pk.txt"


def get_agent_account() -> Optional[LocalAccount]:
    try:
        account = cache.read(AGENT_PK_FILE_NAME)
        if account:
            return cast(LocalAccount, Account.from_key(account))
        return None
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"An error occurred while reading the agent account: {e}")
        raise


def create_agent_account() -> LocalAccount:
    agent_account: str = Account.create().key.hex()
    cache.write(AGENT_PK_FILE_NAME, agent_account)
    return cast(LocalAccount, Account.from_key(agent_account))


def get_or_create_agent_account() -> LocalAccount:
    agent = get_agent_account()
    if agent:
        return agent
    return create_agent_account()


def delete_agent_account() -> None:
    cache.remove(AGENT_PK_FILE_NAME)
