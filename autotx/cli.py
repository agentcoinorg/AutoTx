from dotenv import load_dotenv
load_dotenv()

from eth_account import Account
import time
from web3 import Web3
import uuid
import uvicorn
from typing import cast
import click
import uuid
from eth_account.signers.local import LocalAccount

from autotx.eth_address import ETHAddress
from autotx.utils.ethereum.get_native_balance import get_native_balance
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.utils.constants import SMART_ACCOUNT_OWNER_PK
from autotx.smart_accounts.safe_smart_account import SafeSmartAccount
from autotx.smart_accounts.smart_account import SmartAccount
from autotx.utils.configuration import AppConfig
from autotx.utils.is_dev_env import is_dev_env
from autotx.setup import print_agent_address, setup_agents
from autotx.AutoTx import AutoTx, Config
from autotx.utils.ethereum.helpers.show_address_balances import show_address_balances
from autotx.smart_accounts.smart_account import SmartAccount
from autotx.smart_accounts.local_biconomy_smart_account import LocalBiconomySmartAccount

def print_autotx_info() -> None:
    print("""
    /$$$$$$              /$$            /$$$$$$$$       
    /$$__  $$            | $$           |__  $$__/       
    | $$  \ $$ /$$   /$$ /$$$$$$    /$$$$$$ | $$ /$$   /$$
    | $$$$$$$$| $$  | $$|_  $$_/   /$$__  $$| $$|  $$ /$$/
    | $$__  $$| $$  | $$  | $$    | $$  \ $$| $$ \  $$$$/ 
    | $$  | $$| $$  | $$  | $$ /$$| $$  | $$| $$  >$$  $$ 
    | $$  | $$|  $$$$$$/  |  $$$$/|  $$$$$$/| $$ /$$/\  $$
    |__/  |__/ \______/    \___/   \______/ |__/|__/  \__/

    Source: https://github.com/polywrap/AutoTx
    Support: https://discord.polywrap.io
    """)

@click.group()
def main() -> None:
    pass

def wait_for_native_top_up(web3: Web3, address: ETHAddress) -> None:
    network = NetworkInfo(web3.eth.chain_id)

    print(f"Detected empty account balance.\nTo use your new smart account, please top it up with some native currency.\nSend the funds to: {address} on {network.chain_id.name}")
    print("Waiting...")
    while get_native_balance(web3, address) == 0:
        time.sleep(2)
    print(f"Account balance detected ({get_native_balance(web3, address)}). Ready to use.")

@main.command()
@click.argument('prompt', required=False)
@click.option("-n", "--non-interactive", is_flag=True, help="Non-interactive mode (will not expect further user input or approval)")
@click.option("-v", "--verbose", is_flag=True, help="Verbose mode")
@click.option("-l", "--logs", type=click.Path(exists=False, file_okay=False, dir_okay=True), help="Path to the directory where logs will be stored.")
@click.option("-r", "--max-rounds", type=int, help="Maximum number of rounds to run")
@click.option("-c", "--cache", is_flag=True, help="Use cache for LLM requests")
def run(prompt: str | None, non_interactive: bool, verbose: bool, logs: str | None, max_rounds: int | None, cache: bool | None) -> None:
    print_autotx_info()

    if prompt == None:
        prompt = click.prompt("What do you want to do?")

    app_config = AppConfig()
    wallet: SmartAccount
    if SMART_ACCOUNT_OWNER_PK:
        smart_account_owner = cast(LocalAccount, Account.from_key(SMART_ACCOUNT_OWNER_PK))
        wallet = LocalBiconomySmartAccount(app_config.web3, smart_account_owner, auto_submit_tx=non_interactive)
        print(f"Using Biconomy smart account: {wallet.address}")
        if get_native_balance(app_config.web3, wallet.address) == 0:
            wait_for_native_top_up(app_config.web3, wallet.address)
    else:
        wallet = SafeSmartAccount(app_config.rpc_url, app_config.network_info, auto_submit_tx=non_interactive, fill_dev_account=True)
        print(f"Using Safe smart account: {wallet.address}")

    (get_llm_config, agents, logs_dir) = setup_agents(logs, cache)

    autotx = AutoTx(
        app_config.web3,
        wallet,
        app_config.network_info,
        agents,
        Config(verbose=verbose, get_llm_config=get_llm_config, logs_dir=logs_dir, max_rounds=max_rounds)
    )

    result = autotx.run(cast(str, prompt), non_interactive)

    if result.total_cost_without_cache > 0:
        print(f"LLM cost: ${result.total_cost_without_cache:.2f} (Actual: ${result.total_cost_with_cache:.2f})")
        
    if is_dev_env():
        print("=" * 50)
        print("Final smart account balances:")
        show_address_balances(app_config.web3, app_config.network_info.chain_id, wallet.address)
        print("=" * 50)

@main.command()
@click.option("-v", "--verbose", is_flag=True, help="Verbose mode")
@click.option("-l", "--logs", type=click.Path(exists=False, file_okay=False, dir_okay=True), help="Path to the directory where logs will be stored.")
@click.option("-r", "--max-rounds", type=int, help="Maximum number of rounds to run")
@click.option("-c", "--cache", is_flag=True, help="Use cache for LLM requests")
@click.option("-p", "--port", type=int, help="Port to run the server on")
@click.option("-d", "--dev", is_flag=True, help="Run the server in development mode")
def serve(verbose: bool, logs: str | None, max_rounds: int | None, cache: bool, port: int | None, dev: bool) -> None:
    from autotx.server import setup_server
    
    print_autotx_info()

    setup_server(verbose, logs, max_rounds, cache, dev, check_valid_safe=True)
    uvicorn.run("autotx.server:app", host="localhost", port=port if port else 8000, workers=1)

@main.command()
@click.option("-n", "--name", type=str, help="Name of the application to create")
def new_app(name: str) -> None:
    from autotx import db

    print(f"Creating new application: {name}")

    app = db.create_app(name, uuid.uuid4().hex)

    print(f"Application '{name}' created with API key: {app.api_key}")

@main.group()
def agent() -> None:
    pass

@agent.command(name="address")
def agent_address() -> None:
    print_agent_address()

if __name__ == "__main__":
    main()
