from web3 import Web3

def get_eth_balance(web3: Web3, address: str) -> int: 
    return web3.from_wei(web3.eth.get_balance(address), 'ether')