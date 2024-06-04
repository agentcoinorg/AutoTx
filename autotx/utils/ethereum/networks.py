from dataclasses import dataclass
from typing import cast
from gnosis.eth import EthereumNetwork
from web3 import Web3, HTTPProvider

from autotx.utils.constants import ALCHEMY_API_KEY
from autotx.utils.ethereum.constants import NATIVE_TOKEN_ADDRESS
from autotx.utils.ethereum.helpers.token_list import token_list

ChainId = EthereumNetwork

SUPPORTED_ALCHEMY_NETWORKS: dict[ChainId, str] = {
    ChainId.MAINNET: "eth-mainnet",
    ChainId.GOERLI: "eth-goerli",
    ChainId.SEPOLIA: "eth-sepolia",
    ChainId.OPTIMISM: "opt-mainnet",
    ChainId.OPTIMISM_GOERLI_TESTNET: "opt-goerli",
    ChainId.ARBITRUM_ONE: "arb-mainnet",
    ChainId.ARBITRUM_GOERLI: "arb-goerli",
    ChainId.POLYGON: "polygon-mainnet",
    ChainId.MUMBAI: "polygon-mumbai",
    ChainId.ASTAR: "astar-mainnet",
    ChainId.POLYGON_ZKEVM: "polygonzkevm-mainnet",
    ChainId.POLYGON_ZKEVM_TESTNET: "polygonzkevm-testnet",
    ChainId.BASE_MAINNET: "base-mainnet",
    ChainId.BASE_GOERLI_TESTNET: "base-goerli",
    ChainId.ZKSYNC_V2: "zksync-mainnet",
}

class NetworkInfo:
    chain_id: ChainId
    transaction_service_url: str
    tokens: dict[str, str]

    def __init__(
        self,
        chain_id: int,
    ):
        self.chain_id = ChainId(chain_id)
        config = SUPPORTED_NETWORKS_CONFIGURATION_MAP.get(self.chain_id)

        if not config:
            raise Exception(f"Chain ID {chain_id} is not supported")

        self.transaction_service_url = config.transaction_service_url
        self.tokens = { **self.fetch_tokens_for_chain(chain_id), **config.default_tokens }

    @staticmethod
    def from_chain_id(chain_id: int) -> 'NetworkInfo':
        return NetworkInfo(chain_id)
    
    @staticmethod
    def from_rpc_url(rpc_url: str) -> 'NetworkInfo':
        web3 = Web3(HTTPProvider(rpc_url))
        chain_id = web3.eth.chain_id
        return NetworkInfo(chain_id)

    def fetch_tokens_for_chain(self, chain_id: int) -> dict[str, str]:
        return {
            cast(str, token["symbol"]).lower(): Web3.to_checksum_address(cast(str, token["address"]))
            for token in token_list
            if token["chainId"] == chain_id and Web3.is_checksum_address(cast(str, token["address"]))
        }

    def get_subsidized_rpc_url(self) -> str | None:
        network = SUPPORTED_ALCHEMY_NETWORKS.get(self.chain_id)

        if not network:
            return None

        return f"https://{network}.g.alchemy.com/v2/{ALCHEMY_API_KEY}"

@dataclass
class NetworkConfiguration:
    network_name: str
    transaction_service_url: str
    default_tokens: dict[str, str]


SUPPORTED_NETWORKS_CONFIGURATION_MAP: dict[ChainId, NetworkConfiguration] = {
    ChainId.MAINNET: NetworkConfiguration(
        "Ethereum",
        "https://safe-transaction-mainnet.safe.global/",
        {
            "eth": NATIVE_TOKEN_ADDRESS,
            "usdc": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "dai": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
            "weth": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "wbtc": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
            "usdt": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        },
    ),
    ChainId.OPTIMISM: NetworkConfiguration(
        "Optimism",
        "https://safe-transaction-optimism.safe.global/",
        {
            "eth": NATIVE_TOKEN_ADDRESS,
            "weth": "0x4200000000000000000000000000000000000006",
            "usdc": "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85",
            "dai": "0xda10009cbd5d07dd0cecc66161fc93d7c9000da1",
            "usdt": "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58",
        },
    ),
    ChainId.ZKSYNC_V2: NetworkConfiguration(
        "zkSync",
        "https://safe-transaction-zksync.safe.global/",
        {
            "usdc": "0x3355df6d4c9c3035724fd0e3914de96a5a83aaf4",
            "dai": "0x4b9eb6c0b6ea15176bbf62841c6b2a8a398cb656",
            "usdt": "0x493257fD37EDB34451f62EDf8D2a0C418852bA4C",
        },
    ),
    ChainId.POLYGON: NetworkConfiguration(
        "Polygon PoS",
        "https://safe-transaction-polygon.safe.global/",
        {
            "matic": NATIVE_TOKEN_ADDRESS,
            "wmatic": "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
            "usdc": "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
            "dai": "0x8f3cf7ad23cd3cadbd9735aff958023239c6a063",
            "usdt": "0xc2132d05d31c914a87c6611c10748aeb04b58e8f",
            "wbtc": "0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6"
        },
    ),
    ChainId.BASE_MAINNET: NetworkConfiguration(
        "Base",
        "https://safe-transaction-base.safe.global/",
        {
            "eth": NATIVE_TOKEN_ADDRESS,
            "weth": "0x4200000000000000000000000000000000000006",
            "usdc": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
            "dai": "0x50c5725949a6f0c72e6c4a641f24049a917db0cb",
        },
    ),
    ChainId.ARBITRUM_ONE: NetworkConfiguration(
        "Arbitrum",
        "https://safe-transaction-arbitrum.safe.global/",
        {
            "eth": NATIVE_TOKEN_ADDRESS,
            "weth": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
            "usdc": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
            "dai": "0xda10009cbd5d07dd0cecc66161fc93d7c9000da1",
            "usdt": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
        },
    ),
    ChainId.SEPOLIA: NetworkConfiguration(
        "Sepolia",
        "https://safe-transaction-sepolia.safe.global/",
        {
            "eth": NATIVE_TOKEN_ADDRESS,
            "weth": "0xfff9976782d46cc05630d1f6ebab18b2324d6b14",
        },
    ),
    ChainId.GNOSIS: NetworkConfiguration(
        "Gnosis Chain",
        "https://safe-transaction-gnosis-chain.safe.global",
        {
            "xdai": NATIVE_TOKEN_ADDRESS,
            "wxdai": "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d",
            "usdc": "0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83",
            "cow": "0x177127622c4A00F3d409B75571e12cB3c8973d3c",
            "gno": "0x9C58BAcC331c9aa871AFD802DB6379a98e80CEdb"
        },
    ),
}

SUPPORTED_NETWORKS_AS_STRING = ", ".join(
    [network.name for network in SUPPORTED_NETWORKS_CONFIGURATION_MAP.keys()]
)
