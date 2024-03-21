from web3 import Web3
from web3.types import TxParams
from .get_address import get_address

def build_transfer_eth(web3: Web3, from_address: str, to: str, value: int | float) -> TxParams:
    to = get_address(web3, to)
    from_address = get_address(web3, from_address)
    return {
        "to": to,
        "value": web3.to_wei(value, "ether"),
        "data": b"",
        "from": from_address,
    }
