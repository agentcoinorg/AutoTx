from datetime import datetime
import os
from typing import Any, Callable, Dict, Optional
from eth_account.signers.local import LocalAccount
from gnosis.eth import EthereumClient

from autotx.agents.DelegateResearchTokensAgent import DelegateResearchTokensAgent
from autotx.agents.SendTokensAgent import SendTokensAgent
from autotx.agents.SwapTokensAgent import SwapTokensAgent
from autotx.autotx_agent import AutoTxAgent
from autotx.utils.constants import COINGECKO_API_KEY, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL_NAME
from autotx.utils.ethereum import SafeManager
from autotx.utils.ethereum.cached_safe_address import get_cached_safe_address
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.helpers.fill_dev_account_with_tokens import fill_dev_account_with_tokens
from autotx.utils.ethereum.helpers.get_dev_account import get_dev_account
from autotx.utils.ethereum.helpers.show_address_balances import show_address_balances
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.utils.is_dev_env import is_dev_env
from autotx.utils.ethereum.agent_account import get_or_create_agent_account

def print_agent_address() -> None:
    acc = get_or_create_agent_account()
    print(f"Agent address: {acc.address}")

def setup_safe(smart_account_addr: ETHAddress | None, agent: LocalAccount, client: EthereumClient, fill_dev_account: bool, check_valid_safe: bool) -> SafeManager:
    web3 = client.w3

    chain_id = web3.eth.chain_id

    network_info = NetworkInfo(chain_id)

    if is_dev_env():
        print(f"Connected to fork of {network_info.chain_id.name} network.")
    else:
        print(f"Connected to {network_info.chain_id.name} network.")

    print_agent_address()

    manager: SafeManager

    if smart_account_addr:
        if check_valid_safe and not SafeManager.is_valid_safe(client, smart_account_addr):
            raise Exception(f"Invalid safe address: {smart_account_addr}")

        print(f"Smart account connected: {smart_account_addr}")
        manager = SafeManager.connect(client, smart_account_addr, agent)

        manager.connect_tx_service(network_info.chain_id, network_info.transaction_service_url)
    else:
        print("No smart account connected, deploying a new one...")
        dev_account = get_dev_account()

        is_safe_deployed = get_cached_safe_address()
        manager = SafeManager.deploy_safe(client, dev_account, agent, [dev_account.address, agent.address], 1)
        print(f"Smart account deployed: {manager.address}")
        
        if not is_safe_deployed and fill_dev_account:
            fill_dev_account_with_tokens(client, dev_account, manager.address, network_info)
            print(f"Funds sent to smart account for testing purposes")

        print("=" * 50)
        print("Starting smart account balances:")
        show_address_balances(web3, network_info.chain_id, manager.address)
        print("=" * 50)

    return manager

def setup_agents(logs: str | None, cache: bool | None) -> tuple[Callable[[], Optional[Dict[str, Any]]], list[AutoTxAgent], str | None]:
    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d-%H-%M-%S-') + str(now.microsecond)
    logs_dir = os.path.join(logs, now_str) if logs is not None else None

    get_llm_config = lambda: { 
        "cache_seed": 1 if cache else None, 
        "config_list": [
            {
                "model": OPENAI_MODEL_NAME, 
                "api_key": OPENAI_API_KEY,
                "base_url": OPENAI_BASE_URL
            }
        ]
    }
    agents = [
        SendTokensAgent(),
        SwapTokensAgent()
    ]

    if COINGECKO_API_KEY:
        agents.append(DelegateResearchTokensAgent())

    return (get_llm_config, agents, logs_dir)