from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.types import TxParams

def send_tx(w3: Web3, tx: TxParams, account: LocalAccount) -> bytes:
    tx["from"] = account.address
    if "nonce" not in tx:
        tx["nonce"] = w3.eth.get_transaction_count(
            account.address, block_identifier="pending"
        )

    if "gasPrice" not in tx and "maxFeePerGas" not in tx:
        tx["gasPrice"] = w3.eth.gas_price

    if "gas" not in tx:
        tx["gas"] = w3.eth.estimate_gas(tx)

    signed_tx = account.sign_transaction(tx) # type: ignore
    tx_hash = w3.eth.send_raw_transaction(bytes(signed_tx.rawTransaction))
    print("Send TX: ", tx_hash.hex())
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    assert tx_receipt["status"] == 1, "Error with tx %s - %s" % (tx_hash.hex(), tx)
    return tx_hash
