from web3 import Web3
from gnosis.eth import EthereumNetwork

from autotx.utils.ethereum import get_erc20_balance, get_eth_balance
from autotx.utils.ethereum.constants import NATIVE_TOKEN_ADDRESS
from autotx.utils.ethereum.networks import SUPPORTED_NETWORKS_CONFIGURATION_MAP, NetworkInfo
from autotx.utils.ethereum.eth_address import ETHAddress

def show_address_balances(web3: Web3, network: EthereumNetwork, address: ETHAddress):
    eth_balance = get_eth_balance(web3, address)
    print(f"ETH balance: {eth_balance}")

    tokens = SUPPORTED_NETWORKS_CONFIGURATION_MAP.get(network).default_tokens
    for token in tokens:
        if tokens[token] == NATIVE_TOKEN_ADDRESS:
            continue
        token_address = ETHAddress(tokens[token], web3)
        balance = get_erc20_balance(web3, token_address, address)
        print(f"{token.upper()} balance: {balance}")
