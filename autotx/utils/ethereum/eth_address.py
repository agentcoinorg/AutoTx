from eth_typing import ChecksumAddress
from web3 import HTTPProvider, Web3

from autotx.utils.constants import MAINNET_DEFAULT_RPC

class ETHAddress:
    hex: ChecksumAddress
    ens_domain: str | None

    def __init__(self, hex_or_ens: str):
        if hex_or_ens.endswith(".eth"):
            web3 = Web3(HTTPProvider(MAINNET_DEFAULT_RPC))
            address = web3.ens.address(hex_or_ens)  # type: ignore
            if address == None:
                raise ValueError(f"Invalid ENS: {hex_or_ens}")
            self.hex = address
            self.ens_domain = hex_or_ens
        elif Web3.is_address(hex_or_ens):
            self.hex = Web3.to_checksum_address(hex_or_ens)
            self.ens_domain = None
        else:
            raise ValueError(f"Invalid address: {hex_or_ens}")

    def __repr__(self) -> str:
        return f"{self.ens_domain}({self.hex})" if self.ens_domain else self.hex
