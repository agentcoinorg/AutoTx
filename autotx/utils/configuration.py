import os
import sys
from time import sleep

from web3 import HTTPProvider, Web3
from autotx.get_env_vars import get_env_vars
from eth_typing import URI

from autotx.utils.ethereum.constants import DEVNET_RPC_URL
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.utils.is_dev_env import is_dev_env

smart_account_addr = get_env_vars()

class AppConfig:
    rpc_url: str
    web3: Web3
    network_info: NetworkInfo

    def __init__(
        self,
        subsidized_chain_id: int | None = None, 
    ):
        rpc_url: str

        if subsidized_chain_id:
            network_info = NetworkInfo.from_chain_id(subsidized_chain_id)
            subsidized_rpc_url = network_info.get_subsidized_rpc_url()
            
            if not subsidized_rpc_url:
                raise ValueError(f"Chain ID {subsidized_chain_id} is not supported")
            
            rpc_url = subsidized_rpc_url
        else:
            provided_rpc_url = DEVNET_RPC_URL if is_dev_env() else os.getenv("CHAIN_RPC_URL")

            if not provided_rpc_url:
                sys.exit("CHAIN_RPC_URL is not set")
            
            rpc_url = provided_rpc_url
            
        web3 = Web3(HTTPProvider(rpc_url))
        for i in range(16):
            if web3.is_connected():
                break
            if i == 15:
                if is_dev_env():
                    sys.exit("Can not connect with local node. Did you run `poetry run start-devnet`?")
                else:
                    sys.exit("Can not connect with remote node. Check your CHAIN_RPC_URL")
            sleep(0.5)

        self.rpc_url = rpc_url
        self.web3 = web3
        self.network_info = NetworkInfo(web3.eth.chain_id)
