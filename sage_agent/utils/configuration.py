from sage_agent.get_env_vars import get_env_vars
from gnosis.eth import EthereumClient
from eth_typing import URI
from eth_account import Account

from sage_agent.utils.ethereum import generate_agent_account

rpc_url, user_pk = get_env_vars()


def get_configuration():
    client = EthereumClient(URI(rpc_url))
    user: Account = Account.from_key(user_pk)
    agent: Account = generate_agent_account()

    return (user, agent, client)
