from dotenv import load_dotenv
load_dotenv()
import pytest
from eth_account import Account

from autotx.utils.configuration import AppConfig
from autotx.utils.ethereum.helpers.swap_from_eoa import swap
from autotx.utils.ethereum.send_native import send_native
from autotx.smart_accounts.safe_smart_account import SafeSmartAccount
from autotx.agents.DelegateResearchTokensAgent import DelegateResearchTokensAgent
from autotx.agents.SendTokensAgent import SendTokensAgent
from autotx.agents.SwapTokensAgent import SwapTokensAgent
from autotx.utils.constants import OPENAI_API_KEY, OPENAI_MODEL_NAME
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.eth_address import ETHAddress
from autotx.utils.ethereum.helpers.get_dev_account import get_dev_account
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
def smart_account() -> SafeSmartAccount:
    app_config = AppConfig()
    account = SafeSmartAccount(app_config.rpc_url, app_config.network_info, auto_submit_tx=True)
    dev_account = get_dev_account()

    send_native(dev_account, account.address, 10, app_config.web3)

    return account

@pytest.fixture()
def auto_tx(smart_account):
    network_info = NetworkInfo(smart_account.web3.eth.chain_id)
    get_llm_config = lambda: { "cache_seed": None, "config_list": [{"model": OPENAI_MODEL_NAME, "api_key": OPENAI_API_KEY}]}

    return AutoTx(
        smart_account.web3,
        smart_account,
        network_info, 
        [
            SendTokensAgent(),
            SwapTokensAgent(),
            DelegateResearchTokensAgent()
        ], 
        Config(verbose=True, get_llm_config=get_llm_config, logs_dir=None, log_costs=True, max_rounds=20)
    )

@pytest.fixture()
def usdc(smart_account) -> ETHAddress:
    chain_id = smart_account.web3.eth.chain_id
    network_info = NetworkInfo(chain_id)
    
    eth_address = ETHAddress(network_info.tokens["eth"])
    usdc_address = ETHAddress(network_info.tokens["usdc"])

    amount = 100

    dev_account = get_dev_account()
    swap(smart_account.web3, dev_account, amount, eth_address, usdc_address, network_info.chain_id)
    
    transfer_erc20(smart_account.web3, usdc_address, dev_account, smart_account.address, amount)

    return usdc_address

@pytest.fixture()
def test_accounts() -> list[ETHAddress]:
    # Create 10 random test accounts
    accounts = [ETHAddress(Account.create().address) for _ in range(10)]

    return accounts
