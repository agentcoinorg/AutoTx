from eth_account import Account
from eth_typing import Address
from web3 import Web3
from web3.types import TxReceipt

def send_eth(account: Account, to: str, value: int, web3: Web3) -> tuple[str, TxReceipt]:
    bytes_address: Address = Address(bytes.fromhex(account.address[2:]))

    nonce = web3.eth.get_transaction_count(bytes_address)

    tx = {
        'to': to,
        'value': web3.to_wei(value, 'ether'),
        'gas': 2000000,
        'gasPrice': web3.to_wei('50', 'gwei'),
        'nonce': nonce,
        'chainId': 31337
    }

    signed_tx = account.sign_transaction(tx)

    web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    receipt = web3.eth.wait_for_transaction_receipt(signed_tx.hash)

    return receipt["transactionHash"].hex(), receipt