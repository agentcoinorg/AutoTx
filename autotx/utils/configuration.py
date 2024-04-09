import sys
from time import sleep
from autotx.get_env_vars import get_env_vars
from gnosis.eth import EthereumClient
from eth_typing import URI
from eth_account.signers.local import LocalAccount
from web3 import Web3, HTTPProvider

from autotx.utils.ethereum.agent_account import get_or_create_agent_account
from autotx.utils.ethereum.constants import FORK_RPC_URL
from autotx.utils.ethereum.eth_address import ETHAddress

smart_account_addr = get_env_vars()

def get_configuration() -> tuple[ETHAddress | None, LocalAccount, EthereumClient]:
    w3 = Web3(HTTPProvider(FORK_RPC_URL))
    for i in range(16):
        if w3.is_connected():
            break
        if i == 15:
            sys.exit("Can not connect with local node. Did you run `poetry run start-fork`?")
        sleep(0.5)

    client = EthereumClient(URI(FORK_RPC_URL))
    agent = get_or_create_agent_account()

    smart_account = ETHAddress(smart_account_addr, client.w3) if smart_account_addr else None

    return (smart_account, agent, client)
