from web3 import Web3


def get_address(web3: Web3, address: str):
    if address.endswith(".eth"):
        return web3.ens.address(address) or address
    else:
        return address
