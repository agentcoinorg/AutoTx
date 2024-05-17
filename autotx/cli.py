from dotenv import load_dotenv

from autotx.setup import print_agent_address, setup_agents, setup_safe
from autotx.server import start_server
from autotx.utils.configuration import get_configuration
load_dotenv()

from typing import cast
import click

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
async def run(prompt: str | None, non_interactive: bool, verbose: bool, logs: str | None, max_rounds: int | None, cache: bool | None) -> None:
    print_autotx_info()
    
    if prompt == None:
        prompt = click.prompt("What do you want to do?")

    (smart_account_addr, agent, client) = get_configuration()

    (manager, network_info, web3) = setup_safe(smart_account_addr, agent, client)

    (get_llm_config, agents, logs_dir) = setup_agents(manager, logs, cache)

    autotx = AutoTx(
        manager,
        network_info,
        agents,
        Config(verbose=verbose, logs_dir=logs_dir, max_rounds=max_rounds),
        get_llm_config=get_llm_config,
    )

    result = await autotx.run(cast(str, prompt), non_interactive)

    if result.total_cost_without_cache > 0:
        print(f"LLM cost: ${result.total_cost_without_cache:.2f} (Actual: ${result.total_cost_with_cache:.2f})")
        
    if not smart_account_addr:
        print("=" * 50)
        print("Final smart account balances:")
        show_address_balances(web3, network_info.chain_id, manager.address)
        print("=" * 50)

@main.command()
@click.option("-v", "--verbose", is_flag=True, help="Verbose mode")
@click.option("-l", "--logs", type=click.Path(exists=False, file_okay=False, dir_okay=True), help="Path to the directory where logs will be stored.")
@click.option("-r", "--max-rounds", type=int, help="Maximum number of rounds to run")
@click.option("-c", "--cache", is_flag=True, help="Use cache for LLM requests")
def serve(verbose: bool, logs: str | None, max_rounds: int | None, cache: bool | None) -> None:
    print_autotx_info()
    
    start_server(verbose, logs, max_rounds, cache)

@main.group()
def agent() -> None:
    pass

@agent.command(name="address")
def agent_address() -> None:
    print_agent_address()

if __name__ == "__main__":
    main()
