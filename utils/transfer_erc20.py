from eth_account import Account
from web3 import Web3
from web3.types import TxParams
from web3.middleware import construct_sign_and_send_raw_middleware

from utils.mock_erc20 import MOCK_ERC20_ABI

def transfer_erc20(web3: Web3, token_address: str, from_account: Account, to: str, value: int):
    web3.middleware_onion.add(construct_sign_and_send_raw_middleware(from_account))
   
    MockERC20 = web3.eth.contract(address=token_address, abi=MOCK_ERC20_ABI)

    tx_hash = MockERC20.functions.transfer(to, value).transact({"from": from_account.address})

    return tx_hash