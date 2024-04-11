from eth_account.signers.local import LocalAccount
from eth_typing import Address
from web3 import Web3
from web3.types import TxParams, TxReceipt, Wei

from autotx.utils.ethereum.eth_address import ETHAddress

from .constants import GAS_PRICE_MULTIPLIER

def send_native(account: LocalAccount, to: ETHAddress, value: float, web3: Web3) -> tuple[str, TxReceipt]:
    bytes_address: Address = Address(bytes.fromhex(account.address[2:]))

    nonce = web3.eth.get_transaction_count(bytes_address)

    tx: TxParams = {
        'from': account.address,
        'to': to.hex,
        'value': Wei(int(value * 10 ** 18)),
        'gasPrice': Wei(int(web3.eth.gas_price * GAS_PRICE_MULTIPLIER)),
        'nonce': nonce,
        'chainId': web3.eth.chain_id
    }

    gas = web3.eth.estimate_gas(tx)
    tx.update({'gas': gas})

    signed_tx = account.sign_transaction(tx) # type: ignore

    web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    receipt = web3.eth.wait_for_transaction_receipt(signed_tx.hash)

    return receipt["transactionHash"].hex(), receipt