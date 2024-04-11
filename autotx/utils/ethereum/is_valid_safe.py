from eth_typing import HexStr
from gnosis.eth import EthereumClient
from web3 import Web3
from gnosis.safe import Safe

from autotx.utils.ethereum.eth_address import ETHAddress
from .constants import MASTER_COPY_ADDRESS, MASTER_COPY_L2_ADDRESSES

def is_valid_safe(client: EthereumClient, safe_address: ETHAddress) -> bool:
    w3 = client.w3

    if w3.eth.get_code(Web3.to_checksum_address(safe_address.hex)) != w3.to_bytes(hexstr=HexStr("0x")):
        safe = Safe(Web3.to_checksum_address(safe_address.hex), client)
        master_copy_address = safe.retrieve_master_copy_address()
        return master_copy_address in [MASTER_COPY_ADDRESS] or master_copy_address in MASTER_COPY_L2_ADDRESSES
    else:
        return False