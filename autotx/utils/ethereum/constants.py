from autotx.utils.ethereum.config import contracts_config
from gnosis.eth import EthereumNetwork

MASTER_COPY_ADDRESS = contracts_config["safe"]["master_copy_address"]
PROXY_FACTORY_ADDRESS = contracts_config["safe"]["proxy_factory_address"]
MULTI_SEND_ADDRESS = contracts_config["safe"]["multisend_address"]
GAS_PRICE_MULTIPLIER = 1.1
FORK_RPC_URL = "http://localhost:8545"

class NetworkInfo:
    network: EthereumNetwork
    transaction_service_url: str

    def __init__(self, network: EthereumNetwork, transaction_service_url: str):
        self.network = network
        self.transaction_service_url = transaction_service_url

CHAIN_ID_TO_NETWORK_MAP: dict[int, NetworkInfo] = {
    1: NetworkInfo(EthereumNetwork.MAINNET, "https://safe-transaction-mainnet.safe.global/"),
    11155111: NetworkInfo(EthereumNetwork.SEPOLIA, "https://safe-transaction-sepolia.safe.global/"),
}
