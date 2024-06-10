import uuid
from dotenv import load_dotenv

from autotx import db
from autotx.wallets.safe_smart_wallet import SafeSmartWallet
load_dotenv()
import uvicorn

from typing import cast
import click

from autotx.utils.configuration import AppConfig
from autotx.utils.is_dev_env import is_dev_env
from autotx.setup import print_agent_address, setup_agents
from autotx.server import setup_server
from autotx.AutoTx import AutoTx, Config
from autotx.utils.ethereum.helpers.show_address_balances import show_address_balances

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

    app_config = AppConfig.load(fill_dev_account=True)
    wallet = SafeSmartWallet(app_config.manager, auto_submit_tx=non_interactive)

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
    print_autotx_info()

    setup_server(verbose, logs, max_rounds, cache, dev, check_valid_safe=True)
    uvicorn.run("autotx.server:app", host="localhost", port=port if port else 8000, workers=1)

@main.command()
@click.option("-n", "--name", type=str, help="Name of the application to create")
def new_app(name: str) -> None:
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
