from dotenv import load_dotenv

load_dotenv()

import click
from autotx.agents.SendTokensAgent import SendTokensAgent
from autotx.agents.SwapTokensAgent import SwapTokensAgent
from autotx.AutoTx import AutoTx
from autotx.patch import patch_langchain
from autotx.utils.ethereum.SafeManager import SafeManager
from autotx.utils.ethereum.send_eth import send_eth
from autotx.utils.ethereum.helpers.show_address_balances import show_address_balances
from autotx.utils.configuration import get_configuration

patch_langchain()


@click.command()
@click.option("--prompt", prompt="Prompt", required=True, help="Prompt")
def run(prompt: str):
    (user, agent, client) = get_configuration()
    web3 = client.w3

    manager = SafeManager.deploy_safe(
        client, user, agent, [user.address, agent.address], 1
    )
    # manager.connect_tx_service(EthereumNetwork.SEPOLIA, "https://safe-transaction-sepolia.safe.global/")
    # manager.disconnect_tx_service()

    if web3.eth.get_balance(agent.address) < 1 * 10**18:
        # Send 1 ETH to the agent, so it can execute transactions
        send_eth(user, agent.address, int(1 * 10**18), web3)

    if manager.balance_of(None) < 1 * 10**18:
        # Send 5 ETH to the safe, so it can execute transactions
        send_eth(user, manager.address, int(5 * 10**18), web3)

    show_address_balances(web3, manager.address)

    send_tokens_agent = SendTokensAgent()
    swap_tokens_agent = SwapTokensAgent(client, manager.address)

    autotx = AutoTx(manager, [send_tokens_agent, swap_tokens_agent], None)
    autotx.run(prompt)

    show_address_balances(web3, manager.address)


if __name__ == "__main__":
    run()
