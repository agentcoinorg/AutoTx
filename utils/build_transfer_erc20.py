from web3 import Web3
from web3.types import TxParams
from utils.mock_erc20 import MOCK_ERC20_ABI

def build_transfer_erc20(web3: Web3, token_address: str, from_address: str, to: str, value: int):
    MockERC20 = web3.eth.contract(address=token_address, abi=MOCK_ERC20_ABI)

    tx: TxParams = MockERC20.functions.transfer(to, value).build_transaction({"from": from_address})

    return tx