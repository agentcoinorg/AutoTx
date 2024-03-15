from web3 import Web3
from .mock_erc20 import MOCK_ERC20_ABI

def get_erc20_info(web3: Web3, token_address: str) -> tuple[str, str, int]:
    MockERC20 = web3.eth.contract(address=token_address, abi=MOCK_ERC20_ABI)

    name = MockERC20.functions.name().call()
    symbol = MockERC20.functions.symbol().call()
    decimals = MockERC20.functions.decimals().call()

    return name, symbol, decimals