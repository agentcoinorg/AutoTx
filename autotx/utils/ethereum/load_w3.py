from web3 import Web3
from autotx.utils.ethereum.constants import FORK_RPC_URL

def load_w3() -> Web3:
    web3 = Web3(Web3.HTTPProvider(FORK_RPC_URL))
    return web3