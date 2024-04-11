import os
import sys
from time import sleep

from web3 import Web3
from autotx.get_env_vars import get_env_vars
from gnosis.eth import EthereumClient
from eth_typing import URI
from eth_account.signers.local import LocalAccount

from autotx.utils.ethereum.agent_account import get_or_create_agent_account
from autotx.utils.ethereum.constants import DEVNET_RPC_URL
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.is_dev_env import is_dev_env

smart_account_addr = get_env_vars()

def get_configuration() -> tuple[ETHAddress | None, LocalAccount, EthereumClient]:
    rpc_url = DEVNET_RPC_URL if is_dev_env() else os.getenv("CHAIN_RPC_URL")
    
    if not rpc_url:
        sys.exit("CHAIN_RPC_URL is not set")

    web3 = Web3(Web3.HTTPProvider(rpc_url))

    for i in range(16):
        if web3.is_connected():
            break
        if i == 15:
            if is_dev_env():
                sys.exit("Can not connect with local node. Did you run `poetry run start-devnet`?")
            else:
                sys.exit("Can not connect with remote node. Check your CHAIN_RPC_URL")
        sleep(0.5)

    client = EthereumClient(URI(rpc_url))
    agent = get_or_create_agent_account()

    smart_account = ETHAddress(smart_account_addr, client.w3) if smart_account_addr else None

    return (smart_account, agent, client)
