from autotx.get_env_vars import get_env_vars
from gnosis.eth import EthereumClient
from eth_typing import URI
from eth_account import Account

from autotx.utils.ethereum import generate_agent_account

rpc_url, user_pk, smart_account_addr = get_env_vars()

FORK_RPC_URL = "http://localhost:8545"

def get_configuration():
    client = EthereumClient(URI(FORK_RPC_URL))
    agent: Account = generate_agent_account()

    return (smart_account_addr, agent, client)
