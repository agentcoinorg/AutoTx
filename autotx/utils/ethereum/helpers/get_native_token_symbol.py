from autotx.utils.ethereum.constants import NATIVE_TOKEN_ADDRESS
from autotx.utils.ethereum.networks import SUPPORTED_NETWORKS_CONFIGURATION_MAP, ChainId


def get_native_token_symbol(network: ChainId) -> str:
    current_network = SUPPORTED_NETWORKS_CONFIGURATION_MAP.get(network)
    if not current_network:
        raise Exception(f"Network {network.name} not supported")

    native_token_symbol = next(
        (
            symbol
            for symbol, address in current_network.default_tokens.items()
            if address == NATIVE_TOKEN_ADDRESS
        ),
        None,
    )

    if not native_token_symbol:
        raise Exception(f"Native token not found for network {network.name}")

    return native_token_symbol.upper()
