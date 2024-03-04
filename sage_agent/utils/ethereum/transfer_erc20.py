from eth_account import Account
from web3 import Web3
from web3.types import TxParams
from web3.middleware import construct_sign_and_send_raw_middleware
from .constants import GAS_PRICE_MULTIPLIER

from .mock_erc20 import MOCK_ERC20_ABI

def transfer_erc20(web3: Web3, token_address: str, from_account: Account, to: str, value: int):
    account_middleware = construct_sign_and_send_raw_middleware(from_account)
    web3.middleware_onion.add(account_middleware)
   
    MockERC20 = web3.eth.contract(address=token_address, abi=MOCK_ERC20_ABI)

    tx_hash = MockERC20.functions.transfer(to, value).transact({"from": from_account.address, "gasPrice": int(web3.eth.gas_price * GAS_PRICE_MULTIPLIER)})

    web3.middleware_onion.remove(account_middleware)

    return tx_hash