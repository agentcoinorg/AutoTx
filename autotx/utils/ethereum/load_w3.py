from web3 import Web3
from autotx.get_env_vars import get_env_vars

def load_w3() -> Web3:
    rpc_url, _ = get_env_vars()
    web3 = Web3(Web3.HTTPProvider(rpc_url))
    return web3