from web3 import Web3

from autotx.utils.ethereum.eth_address import ETHAddress
from .erc20_abi import ERC20_ABI

def get_erc20_info(web3: Web3, token_address: ETHAddress) -> tuple[str, str, int]:
    MockERC20 = web3.eth.contract(address=token_address.hex, abi=ERC20_ABI)

    name = MockERC20.functions.name().call()
    symbol = MockERC20.functions.symbol().call()
    decimals = MockERC20.functions.decimals().call()

    return name, symbol, decimals