from autotx.get_env_vars import get_env_vars
from gnosis.eth import EthereumClient
from eth_typing import URI
from eth_account import Account

from autotx.utils.ethereum.agent_account import get_or_create_agent_account
from autotx.utils.ethereum.constants import FORK_RPC_URL

smart_account_addr = get_env_vars()

def get_configuration():
    client = EthereumClient(URI(FORK_RPC_URL))
    agent: Account = get_or_create_agent_account()

    return (smart_account_addr, agent, client)
