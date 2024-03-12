from web3 import Web3
from web3.types import TxParams
from sage_agent.utils.ethereum.mock_erc20 import MOCK_ERC20_ABI


def build_approve_erc20(web3: Web3, token_address: str, spender: str, value: int):
    token_address = web3.to_checksum_address(token_address)
    MockERC20 = web3.eth.contract(address=token_address, abi=MOCK_ERC20_ABI)

    tx: TxParams = MockERC20.functions.approve(spender, value).build_transaction()

    return tx
