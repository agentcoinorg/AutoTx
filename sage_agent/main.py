from dotenv import load_dotenv

load_dotenv()

import click
from sage_agent.agents.erc20 import Erc20Agent
from sage_agent.agents.safe import SafeAgent
from sage_agent.agents.uniswap import UniswapAgent
from sage_agent.sage import Sage
from sage_agent.patch import patch_langchain
from sage_agent.utils.ethereum import deploy_mock_erc20
from sage_agent.utils.ethereum.SafeManager import SafeManager
from sage_agent.utils.ethereum.send_eth import send_eth
from sage_agent.utils.ethereum.helpers.show_address_balances import show_address_balances
from sage_agent.utils.configuration import get_configuration

patch_langchain()


@click.command()
@click.option("--prompt", prompt="Prompt", required=True, help="Prompt")
def run(prompt: str):
    (user, agent, client) = get_configuration()
    web3 = client.w3

    token_address = deploy_mock_erc20(web3, user)

    manager = SafeManager.deploy_safe(
        client, user, agent, [user.address, agent.address], 1
    )
    # manager.connect_tx_service(EthereumNetwork.SEPOLIA, "https://safe-transaction-sepolia.safe.global/")
    # manager.disconnect_tx_service()

    # # Send 1 ETH to the agent, so it can execute transactions
    if manager.balance_of(None) < 1 * 10**18:
        send_eth(user, agent.address, int(1 * 10**18), web3)

    if manager.balance_of(None) < 1 * 10**18:
        # Send 5 ETH to the safe, so it can execute transactions
        send_eth(user, manager.address, int(5 * 10**18), web3)

    show_address_balances(web3, manager.address)

    erc20_agent = Erc20Agent([token_address])
    safe_agent = SafeAgent(manager, agent)
    uniswap_agent = UniswapAgent(client, manager.address)

    sage = Sage([erc20_agent, safe_agent, uniswap_agent], None)

    sage.run(prompt)

    show_address_balances(web3, manager.address)


if __name__ == "__main__":
    run()
