from web3 import Web3
from web3.types import TxParams

from autotx.utils.ethereum.eth_address import ETHAddress

def build_transfer_native(web3: Web3, from_address: ETHAddress, to: ETHAddress, value: float) -> TxParams:
    return {
        "to": to.hex,
        "value": web3.to_wei(value, "ether"),
        "data": b"",
        "from": from_address.hex,
    }
