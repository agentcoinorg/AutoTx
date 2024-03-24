from web3 import Web3

class ETHAddress:
    hex: str
    ens_domain: str | None

    def __init__(self, hex_or_ens: str, web3: Web3):
        if hex_or_ens.endswith(".eth"):
            self.hex = web3.ens.address(hex_or_ens)
            self.ens_domain = hex_or_ens
        elif Web3.is_address(hex_or_ens):
            self.hex = Web3.to_checksum_address(hex_or_ens)
            self.ens_domain = None
        else:
            raise ValueError(f"Invalid address: {hex_or_ens}")
        
    def __repr__(self) -> str:
        return f"{self.ens_domain}({self.hex})" if self.ens_domain else self.hex
