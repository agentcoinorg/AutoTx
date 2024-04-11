import os
from web3 import Web3
from autotx.utils.ethereum.constants import DEVNET_RPC_URL
from autotx.utils.is_dev_env import is_dev_env

def load_w3() -> Web3:
    rpc_url = DEVNET_RPC_URL if is_dev_env() else os.getenv("CHAIN_RPC_URL")
    
    web3 = Web3(Web3.HTTPProvider(rpc_url))
    
    return web3