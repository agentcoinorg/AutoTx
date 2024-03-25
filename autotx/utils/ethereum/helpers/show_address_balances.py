from web3 import Web3

from autotx.utils.ethereum import get_erc20_balance
from autotx.utils.ethereum.constants import NetworkInfo

def show_address_balances(web3: Web3, network: NetworkInfo, address: str):
    eth_balance = web3.eth.get_balance(Web3.to_checksum_address(address))
    print(f"ETH balance: {eth_balance / 10 ** 18}")

    tokens = network.tokens
    for token in tokens:
        token_address = tokens[token]
        balance = get_erc20_balance(web3, token_address, address)
        print(f"{token.upper()} balance: {balance / 10 ** 18}")
