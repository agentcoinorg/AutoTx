import click
from dotenv import load_dotenv
from eth_account import Account

from autotx.utils.ethereum.constants import CHAIN_ID_TO_NETWORK_MAP
from autotx.utils.ethereum.helpers.get_test_account import get_test_account
load_dotenv()
from autotx.agents import SendTokensAgent
from autotx.agents import SwapTokensAgent
from autotx.AutoTx import AutoTx
from autotx.patch import patch_langchain
from autotx.utils.ethereum import generate_agent_account, delete_agent_account
from autotx.utils.ethereum.SafeManager import SafeManager
from autotx.utils.ethereum.send_eth import send_eth
from autotx.utils.ethereum.helpers.show_address_balances import show_address_balances
from autotx.utils.configuration import get_configuration

patch_langchain()

@click.group()
def main():
    pass

@main.command()
@click.option("--prompt", prompt="Prompt", required=True, help="Prompt")
@click.option("--headless", is_flag=True, help="Headless mode (will not expect further user input or approval)")
@click.option("--strict", is_flag=True, help="Strict mode (will ask for more information if needed)")
def run(prompt: str, headless: bool, strict: bool):
    (smart_account_addr, agent, client) = get_configuration()
    web3 = client.w3

    chain_id = web3.eth.chain_id
    print(f"Chain ID: {chain_id}")

    network_info = CHAIN_ID_TO_NETWORK_MAP.get(chain_id)

    if network_info is None:
        raise Exception(f"Chain ID {chain_id} is not supported")

    manager: SafeManager

    if smart_account_addr:
        if not SafeManager.is_valid_safe(client, smart_account_addr):
            raise Exception(f"Invalid safe address: {smart_account_addr}")

        print(f"Smart account connected: {smart_account_addr}")
        manager = SafeManager.connect(client, smart_account_addr, agent)

        manager.connect_tx_service(network_info.network, network_info.transaction_service_url)
    else:
        print("No smart account connected, deploying a new one...")
        user_test_account = get_test_account()

        manager = SafeManager.deploy_safe(client, user_test_account, agent, [user_test_account.address, agent.address], 1)
        send_eth(user_test_account, manager.address, int(0.1 * 10**18), web3)
        print(f"Smart account deployed: {manager.address}")

    print("Starting smart account balances:")
    show_address_balances(web3, manager.address)

    autotx = AutoTx(manager, [
        SendTokensAgent.build_agent_factory(),
        SwapTokensAgent.build_agent_factory(client, manager.address),
    ], None)
    autotx.run(prompt, headless, strict)

    print("Final smart account balances:")
    show_address_balances(web3, manager.address)

@main.group()
def agent():
    pass

@agent.group(name="account")
def agent_account():
    pass

@agent_account.command(name="create")
def agent_account_create():
    print("Creating agent account...")
    agent_acc = generate_agent_account()
    print(f"Agent account created with address {agent_acc.address}")

@agent_account.command(name="delete")
def agent_account_delete():
    print("Deleting agent account...")
    delete_agent_account()
    print("Agent account deleted")

@agent_account.command(name="info")
def agent_account_info():
    (_user, agent, client, _safe_address) = get_configuration()
    web3 = client.w3
    print(f"Agent address: {agent.address}")
    show_address_balances(web3, agent.address)

if __name__ == "__main__":
    main()
