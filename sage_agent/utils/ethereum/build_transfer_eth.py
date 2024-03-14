from web3 import Web3
from web3.types import TxParams

def build_transfer_eth(web3: Web3, from_address: str, to: str, value: int | float) -> TxParams:
    tx = {
        "to": to,
        "value": web3.to_wei(value, "ether"),
        "data": b"",
        "from": from_address,
    }

    return tx