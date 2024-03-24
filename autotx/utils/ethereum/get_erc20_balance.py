from web3 import Web3

from autotx.utils.ethereum.eth_address import ETHAddress
from .mock_erc20 import MOCK_ERC20_ABI

def get_erc20_balance(web3: Web3, token_address: ETHAddress, account: ETHAddress) -> int:
    MockERC20 = web3.eth.contract(address=Web3.to_checksum_address(token_address.hex), abi=MOCK_ERC20_ABI)
    return MockERC20.functions.balanceOf(account.hex).call()
