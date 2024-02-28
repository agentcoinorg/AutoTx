from eth_account import Account
from eth_typing import Address
from web3 import Web3
from web3.types import TxReceipt

from utils.constants import GAS_PRICE_MULTIPLIER

def send_eth(account: Account, to: str, value: int, web3: Web3) -> tuple[str, TxReceipt]:
    bytes_address: Address = Address(bytes.fromhex(account.address[2:]))

    nonce = web3.eth.get_transaction_count(bytes_address)

    tx = {
        'to': to,
        'value': value,
        'gas': 30000, # TODO: Estimate gas
        'gasPrice': int(web3.eth.gas_price * GAS_PRICE_MULTIPLIER),
        'nonce': nonce,
        'chainId': web3.eth.chain_id
    }

    signed_tx = account.sign_transaction(tx)

    web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    print("Send ETH (" + str(int(value / 10 ** 18)) + ") TX: ", signed_tx.hash.hex())

    receipt = web3.eth.wait_for_transaction_receipt(signed_tx.hash)

    return receipt["transactionHash"].hex(), receipt