from autotx.get_env_vars import get_env_vars
from gnosis.eth import EthereumClient
from eth_typing import URI
from eth_account import Account

from autotx.utils.ethereum import generate_agent_account
from autotx.utils.ethereum.get_cached_safe_address import get_cached_safe_address

rpc_url, user_pk = get_env_vars()


def get_configuration():
    client = EthereumClient(URI(rpc_url))
    user: Account = Account.from_key(user_pk)
    agent: Account = generate_agent_account()
    safe_address = get_cached_safe_address()

    return (user, agent, client, safe_address)
