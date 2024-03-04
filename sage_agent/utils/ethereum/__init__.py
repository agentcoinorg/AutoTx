from .deploy_safe import deploy_safe
from .get_eth_balance import get_eth_balance
from .send_eth import send_eth
from .deploy_safe_with_create2 import deploy_safe_with_create2
from .generate_agent_account import generate_agent_account
from .constants import MASTER_COPY_ADDRESS, PROXY_FACTORY_ADDRESS, MULTI_SEND_ADDRESS, GAS_PRICE_MULTIPLIER
from .deploy_multicall import deploy_multicall
from .send_tx import send_tx
from .cache import cache
from .deploy_mock_erc20 import deploy_mock_erc20
from .transfer_erc20 import transfer_erc20
from .build_transfer_eth import build_transfer_eth
from .build_transfer_erc20 import build_transfer_erc20
from .get_erc20_balance import get_erc20_balance
from .SafeManager import SafeManager
from web3 import Web3

provider = Web3.HTTPProvider(f"https://sepolia.infura.io/v3/0bb7b9fb2c90413bbc4198ad6cfb87b1")

__all__ = [
    "provider",
    "deploy_safe",
    "get_eth_balance",
    "send_eth",
    "deploy_safe_with_create2",
    "generate_agent_account",
    "MASTER_COPY_ADDRESS",
    "PROXY_FACTORY_ADDRESS",
    "MULTI_SEND_ADDRESS",
    "GAS_PRICE_MULTIPLIER",
    "deploy_multicall",
    "send_tx",
    "cache",
    "deploy_mock_erc20",
    "transfer_erc20",
    "build_transfer_eth",
    "build_transfer_erc20",
    "get_erc20_balance",
    "SafeManager",
]