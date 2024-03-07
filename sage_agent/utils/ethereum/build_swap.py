from gnosis.eth.oracles import UniswapV3Oracle
from gnosis.eth.oracles.abis.uniswap_v3 import uniswap_v3_router_abi

def get_pool() -> str:
    oracle = UniswapV3Oracle()
    # oracle.