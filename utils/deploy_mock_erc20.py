from eth_account import Account
from web3 import Web3
from web3.types import TxParams
from web3.middleware import construct_sign_and_send_raw_middleware

from utils.mock_erc20 import MOCK_ERC20_ABI, MOCK_ERC20_BYTECODE

def deploy_mock_erc20(web3: Web3, account: Account) -> str:
    account_middleware = construct_sign_and_send_raw_middleware(account)
    web3.middleware_onion.add(account_middleware)
    MockERC20 = web3.eth.contract(abi=MOCK_ERC20_ABI, bytecode=MOCK_ERC20_BYTECODE)

    tx_hash = MockERC20.constructor().transact({"from": account.address, "gasPrice": web3.eth.gas_price})

    print("Deploying Mock ERC20 TX: ", tx_hash.hex())

    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    web3.middleware_onion.remove(account_middleware)

    return receipt.contractAddress