from web3 import Web3

from autotx.utils.ethereum.eth_address import ETHAddress
from .erc20_abi import ERC20_ABI

def get_erc20_info(web3: Web3, token_address: ETHAddress) -> tuple[str, str, int]:
    erc20 = web3.eth.contract(address=token_address.hex, abi=ERC20_ABI)

    name = erc20.functions.name().call()
    symbol = erc20.functions.symbol().call()
    decimals = erc20.functions.decimals().call()

    return name, symbol, decimals