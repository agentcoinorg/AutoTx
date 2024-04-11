import os
import sys
from web3 import Web3
from autotx.utils.ethereum.constants import DEVNET_RPC_URL
from autotx.utils.is_dev_env import is_dev_env

def load_w3() -> Web3:
    rpc_url = DEVNET_RPC_URL if is_dev_env() else os.getenv("CHAIN_RPC_URL")
    
    if not rpc_url:
        sys.exit("CHAIN_RPC_URL is not set")

    web3 = Web3(Web3.HTTPProvider(rpc_url))
    
    return web3