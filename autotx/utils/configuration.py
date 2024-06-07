import os
import sys
from time import sleep

from web3 import Web3
from autotx.get_env_vars import get_env_vars
from gnosis.eth import EthereumClient
from eth_typing import URI
from eth_account.signers.local import LocalAccount

from autotx.setup import setup_safe
from autotx.utils.ethereum import SafeManager
from autotx.utils.ethereum.agent_account import get_or_create_agent_account
from autotx.utils.ethereum.constants import DEVNET_RPC_URL
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.utils.is_dev_env import is_dev_env
from autotx.wallets.smart_wallet import SmartWallet

smart_account_addr = get_env_vars()

class AppConfig:
    web3: Web3
    client: EthereumClient
    agent: LocalAccount
    manager: SafeManager
    network_info: NetworkInfo

    def __init__(
        self,
        web3: Web3,
        client: EthereumClient,
        agent: LocalAccount,
        manager: SafeManager,
        network_info: NetworkInfo,
    ):
        self.web3 = web3
        self.client = client
        self.agent = agent
        self.manager = manager
        self.network_info = network_info

    @staticmethod
    def load(
        smart_account_addr: str | None = None,
        subsidized_chain_id: int | None = None, 
        fill_dev_account: bool = False,
        agent: LocalAccount | None = None,
        check_valid_safe: bool = False,
    ) -> "AppConfig":
        rpc_url: str

        if subsidized_chain_id:
            network_info = NetworkInfo.from_chain_id(subsidized_chain_id)
            subsidized_rpc_url = network_info.get_subsidized_rpc_url()
            
            if not subsidized_rpc_url:
                raise ValueError(f"Chain ID {subsidized_chain_id} is not supported")
            
            rpc_url = subsidized_rpc_url
        else:
            provided_rpc_url = DEVNET_RPC_URL if is_dev_env() else os.getenv("CHAIN_RPC_URL")

            if not provided_rpc_url:
                sys.exit("CHAIN_RPC_URL is not set")
            
            rpc_url = provided_rpc_url
            
        client = EthereumClient(URI(rpc_url))

        for i in range(16):
            if client.w3.is_connected():
                break
            if i == 15:
                if is_dev_env():
                    sys.exit("Can not connect with local node. Did you run `poetry run start-devnet`?")
                else:
                    sys.exit("Can not connect with remote node. Check your CHAIN_RPC_URL")
            sleep(0.5)

        agent = agent if agent else get_or_create_agent_account()

        smart_account_addr = smart_account_addr if smart_account_addr else os.getenv("SMART_ACCOUNT_ADDRESS")
        smart_account = ETHAddress(smart_account_addr) if smart_account_addr else None
        
        manager = setup_safe(smart_account, agent, client, fill_dev_account, check_valid_safe)

        return AppConfig(client.w3, client, agent, manager, NetworkInfo(client.w3.eth.chain_id))
