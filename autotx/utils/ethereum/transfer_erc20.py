from eth_account import Account
from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware

from autotx.utils.ethereum.get_address import get_address
from .constants import GAS_PRICE_MULTIPLIER

from .mock_erc20 import MOCK_ERC20_ABI

def transfer_erc20(web3: Web3, token_address: str, from_account: Account, to: str, value: float):
    account_middleware = construct_sign_and_send_raw_middleware(from_account)
    web3.middleware_onion.add(account_middleware)

    to = get_address(web3, to)
   
    erc20 = web3.eth.contract(address=token_address, abi=MOCK_ERC20_ABI)
    decimals = erc20.functions.decimals().call()

    tx_hash = erc20.functions.transfer(to, int(value * 10 ** decimals)).transact({"from": from_account.address, "gasPrice": int(web3.eth.gas_price * GAS_PRICE_MULTIPLIER)})

    web3.middleware_onion.remove(account_middleware)

    return tx_hash