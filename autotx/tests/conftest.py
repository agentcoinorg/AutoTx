import time
from dotenv import load_dotenv

from autotx.utils.ethereum.cached_safe_address import delete_cached_safe_address
from autotx.utils.ethereum.constants import SUPPORTED_NETWORKS
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.helpers.get_dev_account import get_dev_account

load_dotenv()

import pytest

from autotx.agents import SendTokensAgent
from autotx.agents import SwapTokensAgent
from autotx.AutoTx import AutoTx
from autotx.chain_fork import stop, start
from autotx.utils.configuration import get_configuration
from autotx.utils.ethereum import (
    SafeManager,
    deploy_mock_erc20,
    send_eth,
    transfer_erc20,
)

@pytest.fixture(autouse=True)
def start_and_stop_local_fork():
    start()

    yield

    stop()

@pytest.fixture()
def configuration():
    (_, agent, client) = get_configuration()
    dev_account = get_dev_account()
    delete_cached_safe_address()

    manager = SafeManager.deploy_safe(
        client, dev_account, agent, [dev_account.address, agent.address], 1
    )

    # Send 10 ETH to the smart account for tests
    send_eth(dev_account, manager.address, 10, client.w3)

    return (dev_account, agent, client, manager)

@pytest.fixture()
def auto_tx(configuration):
    (_, _, client, manager) = configuration
    network_info = SUPPORTED_NETWORKS.get(client.w3.eth.chain_id)

    return AutoTx(manager, network_info, [
        SendTokensAgent.build_agent_factory(),
        SwapTokensAgent.build_agent_factory(client, manager.address),
    ], None)

@pytest.fixture()
def mock_erc20(configuration) -> ETHAddress:
    (user, _, client, manager) = configuration
    mock_erc20 = deploy_mock_erc20(client.w3, user)
    transfer_tx = transfer_erc20(
        client.w3, mock_erc20, user, manager.address, 100
    )
    manager.wait(transfer_tx)

    chain_id = client.w3.eth.chain_id
    network = SUPPORTED_NETWORKS.get(chain_id)

    network.tokens["ttok"] = mock_erc20.hex

    return mock_erc20
