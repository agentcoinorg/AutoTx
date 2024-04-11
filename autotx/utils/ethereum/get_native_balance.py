from web3 import Web3

from autotx.utils.ethereum.eth_address import ETHAddress

def get_native_balance(web3: Web3, address: ETHAddress) -> float: 
    return web3.eth.get_balance(address.hex) / 10 ** 18