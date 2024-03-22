from dotenv import load_dotenv

from autotx.utils.ethereum.helpers.get_test_account import get_test_account

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
from autotx.utils.ethereum.config import contracts_config

@pytest.fixture(autouse=True)
def start_and_stop_local_fork():
    start()
    (_, agent, client) = get_configuration()
    user = get_test_account()
    
    manager = SafeManager.deploy_safe(
        client, user, agent, [user.address, agent.address], 1
    )

    send_eth(user, manager.address, int(5 * 10**18), client.w3)

    yield

    stop()

@pytest.fixture()
def configuration():
    (_, agent, client) = get_configuration()
    user = get_test_account()

    manager = SafeManager.deploy_safe(
        client, user, agent, [user.address, agent.address], 1
    )

    return (user, agent, client, manager)

@pytest.fixture()
def auto_tx(configuration):
    (_, _, client, manager) = configuration

    return AutoTx(manager, [
        SendTokensAgent.build_agent_factory(),
        SwapTokensAgent.build_agent_factory(client, manager.address),
    ], None)

@pytest.fixture()
def mock_erc20(configuration):
    (user, _, client, manager) = configuration
    mock_erc20 = deploy_mock_erc20(client.w3, user)
    transfer_tx = transfer_erc20(
        client.w3, mock_erc20, user, manager.address, int(100 * 10**18)
    )
    manager.wait(transfer_tx)
    contracts_config["erc20"]["tt"] = mock_erc20

    return mock_erc20
