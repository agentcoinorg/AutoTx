import os
from dotenv import load_dotenv

from autotx.utils.ethereum import generate_agent_account, delete_agent_account
from autotx.utils.ethereum.cached_safe_address import delete_cached_safe_address, save_cached_safe_address
from autotx.utils.ethereum.is_valid_safe import is_valid_safe

load_dotenv()

import click
from autotx.agents import SendTokensAgent
from autotx.agents import SwapTokensAgent
from autotx.AutoTx import AutoTx
from autotx.patch import patch_langchain
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
def run(prompt: str):
    (user, agent, client, safe_address) = get_configuration()
    web3 = client.w3

    manager: SafeManager

    if safe_address != None and SafeManager.is_valid_safe(client, safe_address):
        print(f"Safe address connected: {safe_address}")
        manager = SafeManager.connect(client, safe_address, agent)
    else:
        manager = SafeManager.deploy_safe(client, user, agent, [user.address, agent.address], 1)

    # manager.connect_tx_service(EthereumNetwork.SEPOLIA, "https://safe-transaction-sepolia.safe.global/")
    # manager.disconnect_tx_service()

    if web3.eth.get_balance(agent.address) < 1 * 10**18:
        # Send 1 ETH to the agent, so it can execute transactions
        send_eth(user, agent.address, int(1 * 10**18), web3)

    if manager.balance_of(None) < 1 * 10**18:
        # Send 5 ETH to the safe, so it can execute transactions
        send_eth(user, manager.address, int(5 * 10**18), web3)

    show_address_balances(web3, manager.address)

    autotx = AutoTx(manager, [
        SendTokensAgent.build_agent_factory(),
        SwapTokensAgent.build_agent_factory(client, manager.address),
    ], None)
    autotx.run(prompt)

    show_address_balances(web3, manager.address)

@main.group()
def safe():
    pass

@safe.command(name="connect")
@click.option("--address", prompt="Address", required=True, help="Safe address")
def safe_connect(address: str):
    (_user, _agent, client, _safe_address) = get_configuration()
    is_valid_safe = SafeManager.is_valid_safe(client, address)
    if is_valid_safe:
        save_cached_safe_address(address)

        print(f"Safe address connected: {address}")
        show_address_balances(client.w3, address)
        print("Make sure to add the agent account to the safe as a signer (and update the treshold to 1/X) to be able to execute transactions")
    else:
        print("The address you provided is not a valid safe address")

@safe.command(name="disconnect")
def safe_disconnect():
    result = delete_cached_safe_address()
    if result:
        print("Safe address disconnected")
    else:
        print("No safe address was connected")

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
