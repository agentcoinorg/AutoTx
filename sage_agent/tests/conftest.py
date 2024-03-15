from dotenv import load_dotenv
load_dotenv()

import pytest

from sage_agent.agents.erc20 import Erc20Agent
from sage_agent.agents.uniswap import UniswapAgent
from sage_agent.sage import Sage
from sage_agent.scripts.local_environment import reset, start
from sage_agent.utils.configuration import get_configuration
from sage_agent.utils.ethereum import (
    SafeManager,
    deploy_mock_erc20,
    send_eth,
    transfer_erc20,
)
from sage_agent.utils.ethereum.config import contracts_config


@pytest.fixture(autouse=True)
def start_and_stop_local_fork():
    start()
    (user, agent, client) = get_configuration()

    manager = SafeManager.deploy_safe(
        client, user, agent, [user.address, agent.address], 1
    )

    send_eth(user, agent.address, int(0.1 * 10**18), client.w3)
    send_eth(user, user.address, int(5 * 10**18), client.w3)
    send_eth(user, manager.address, int(5 * 10**18), client.w3)

    yield

    reset()


@pytest.fixture()
def configuration():
    (user, agent, client) = get_configuration()

    manager = SafeManager.deploy_safe(
        client, user, agent, [user.address, agent.address], 1
    )

    return (user, agent, client, manager)


@pytest.fixture()
def auto_tx(configuration):
    (_, _, client, manager) = configuration

    erc20_agent = Erc20Agent()
    uniswap_agent = UniswapAgent(client, manager.address)

    return Sage(manager, [erc20_agent, uniswap_agent], None)


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
