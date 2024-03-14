from dotenv import load_dotenv
load_dotenv()

import pytest

from sage_agent.utils.configuration import get_configuration
from sage_agent.utils.ethereum import SafeManager

@pytest.fixture()
def configuration():
    (user, agent, client) = get_configuration()

    manager = SafeManager.deploy_safe(
        client, user, agent, [user.address, agent.address], 1
    )

    return (user, agent, client, manager)