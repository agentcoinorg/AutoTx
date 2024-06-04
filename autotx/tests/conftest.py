from dotenv import load_dotenv

from autotx.utils.configuration import AppConfig
from autotx.utils.ethereum.helpers.swap_from_eoa import swap
from autotx.utils.ethereum.send_native import send_native
from autotx.wallets.safe_smart_wallet import SafeSmartWallet
load_dotenv()

from autotx.agents.DelegateResearchTokensAgent import DelegateResearchTokensAgent
from autotx.agents.SendTokensAgent import SendTokensAgent
from autotx.agents.SwapTokensAgent import SwapTokensAgent

from eth_account import Account

from autotx.utils.constants import OPENAI_API_KEY, OPENAI_MODEL_NAME
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.helpers.get_dev_account import get_dev_account

import pytest
from autotx.AutoTx import AutoTx, Config
from autotx.chain_fork import stop, start
from autotx.utils.ethereum import (
    transfer_erc20,
)

@pytest.fixture(autouse=True)
def start_and_stop_local_fork():
    start()

    yield

    stop()

@pytest.fixture()
def configuration():
    app_config = AppConfig.load()
    wallet = SafeSmartWallet(app_config.manager, auto_submit_tx=True)
    dev_account = get_dev_account()

    send_native(dev_account, wallet.address, 10, app_config.web3)

    return (dev_account, app_config.agent, app_config.client, app_config.manager, wallet)

@pytest.fixture()
def auto_tx(configuration):
    (_, _, client, _, wallet) = configuration
    network_info = NetworkInfo(client.w3.eth.chain_id)
    get_llm_config = lambda: { "cache_seed": None, "config_list": [{"model": OPENAI_MODEL_NAME, "api_key": OPENAI_API_KEY}]}

    return AutoTx(
        client.w3,
        wallet,
        network_info, 
        [
            SendTokensAgent(),
            SwapTokensAgent(),
            DelegateResearchTokensAgent()
        ], 
        Config(verbose=True, get_llm_config=get_llm_config, logs_dir=None, log_costs=True, max_rounds=100), 
    )

@pytest.fixture()
def usdc(configuration) -> ETHAddress:
    (user, _, client, _, wallet) = configuration
 
    chain_id = client.w3.eth.chain_id
    network_info = NetworkInfo(chain_id)
    
    eth_address = ETHAddress(network_info.tokens["eth"])
    usdc_address = ETHAddress(network_info.tokens["usdc"])

    amount = 100

    swap(client, user, amount, eth_address, usdc_address, network_info.chain_id)
    
    transfer_erc20(client.w3, usdc_address, user, wallet.address, amount)

    return usdc_address

@pytest.fixture()
def test_accounts() -> list[ETHAddress]:
    # Create 10 random test accounts
    accounts = [ETHAddress(Account.create().address) for _ in range(10)]

    return accounts
