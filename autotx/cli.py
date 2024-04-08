from dotenv import load_dotenv
load_dotenv()

import click
from autotx.utils.constants import OPENAI_API_KEY, OPENAI_MODEL_NAME
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.utils.ethereum.helpers.get_dev_account import get_dev_account
from autotx.AutoTx import AutoTx
from autotx.patch import patch_langchain
from autotx.utils.ethereum.agent_account import get_agent_account, create_agent_account, delete_agent_account
from autotx.utils.ethereum.SafeManager import SafeManager
from autotx.utils.ethereum.send_eth import send_eth
from autotx.utils.ethereum.helpers.show_address_balances import show_address_balances
from autotx.utils.configuration import get_configuration
from autotx.agents import ResearchTokensAgent, SendTokensAgent, SwapTokensAgent

patch_langchain()

@click.group()
def main():
    pass

@main.command()
@click.argument('prompt', required=False)
@click.option("-n", "--non-interactive", is_flag=True, help="Non-interactive mode (will not expect further user input or approval)")
def run(prompt: str | None, non_interactive: bool):
    if prompt == None:
        prompt = click.prompt("What do you want to do?")

    (smart_account_addr, agent, client) = get_configuration()
    web3 = client.w3

    print_agent_address()

    chain_id = web3.eth.chain_id
    print(f"Chain ID: {chain_id}")

    network_info = NetworkInfo(chain_id)

    manager: SafeManager

    if smart_account_addr:
        if not SafeManager.is_valid_safe(client, smart_account_addr):
            raise Exception(f"Invalid safe address: {smart_account_addr}")

        print(f"Smart account connected: {smart_account_addr}")
        manager = SafeManager.connect(client, smart_account_addr, agent)

        manager.connect_tx_service(network_info.chain_id, network_info.transaction_service_url)
    else:
        print("No smart account connected, deploying a new one...")
        dev_account = get_dev_account()

        manager = SafeManager.deploy_safe(client, dev_account, agent, [dev_account.address, agent.address], 1)
        print(f"Smart account deployed: {manager.address}")
        
        send_eth(dev_account, manager.address, 10, web3)
        print(f"Sent 10 ETH to smart account for testing purposes")

        print("Starting smart account balances:")
        show_address_balances(web3, network_info.chain_id, manager.address)

    get_llm_config = lambda: { "cache_seed": None, "config_list": [{"model": OPENAI_MODEL_NAME, "api_key": OPENAI_API_KEY}]}
    autotx = AutoTx(
        manager, 
        network_info, 
        [
            SendTokensAgent.build_agent_factory(),
            SwapTokensAgent.build_agent_factory(),
            ResearchTokensAgent.build_agent_factory()
        ], 
        None, get_llm_config=get_llm_config
    )

    autotx.run(prompt, non_interactive)

    if not smart_account_addr:
        print("Final smart account balances:")
        show_address_balances(web3, network_info.chain_id, manager.address)

@main.group()
def agent():
    pass

@agent.command(name="address")
def agent_address():
    print_agent_address()

def print_agent_address():
    acc = get_agent_account()

    if acc == None:
        acc = create_agent_account()

    print(f"Agent address: {acc.address}")

if __name__ == "__main__":
    main()
