from web3 import Web3

from autotx.utils.ethereum import get_erc20_balance, get_native_balance
from autotx.utils.ethereum.constants import NATIVE_TOKEN_ADDRESS
from autotx.utils.ethereum.networks import SUPPORTED_NETWORKS_CONFIGURATION_MAP, ChainId
from autotx.utils.ethereum.eth_address import ETHAddress


def show_address_balances(web3: Web3, network: ChainId, address: ETHAddress) -> None:
    current_network = SUPPORTED_NETWORKS_CONFIGURATION_MAP.get(network)

    if current_network:
        native_token_symbol = next(
            (
                symbol
                for symbol, address in current_network.default_tokens.items()
                if address == NATIVE_TOKEN_ADDRESS
            ),
            None,
        )
        if native_token_symbol:
            native_token_balance = get_native_balance(web3, address)
            print(f"{native_token_symbol.upper()} balance: {native_token_balance}")
        for token in current_network.default_tokens:
            if current_network.default_tokens[token] == NATIVE_TOKEN_ADDRESS:
                continue
            token_address = ETHAddress(current_network.default_tokens[token])
            balance = get_erc20_balance(web3, token_address, address)

            if balance > 0:
                print(f"{token.upper()} balance: {balance}")
