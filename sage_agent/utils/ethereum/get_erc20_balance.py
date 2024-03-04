from web3 import Web3
from sage_agent.utils.ethereum.mock_erc20 import MOCK_ERC20_ABI

def get_erc20_balance(web3: Web3, token_address: str, account: str) -> int:
    MockERC20 = web3.eth.contract(address=token_address, abi=MOCK_ERC20_ABI)

    return MockERC20.functions.balanceOf(account).call()