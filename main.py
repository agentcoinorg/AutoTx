import os
import click
from dotenv import load_dotenv
from eth_account import Account
from eth_typing import URI
from gnosis.eth import EthereumClient
from gnosis.eth.multicall import Multicall

from utils import deploy_multicall, deploy_safe_with_create2, generate_agent_account, get_eth_balance, send_eth

load_dotenv()

def get_env_vars() -> tuple[str, str, str, str, str]:
    rpc_url = os.getenv("RPC_URL")
    if not rpc_url:
        raise ValueError("RPC_URL is not set")

    user_pk = os.getenv("USER_PRIVATE_KEY")
    if not user_pk:
        raise ValueError("USER_PRIVATE_KEY is not set")

    return rpc_url, user_pk

@click.command()
@click.option('--prompt',
    prompt='Prompt',
    required=True,
    help='Prompt'
)
def run(
    prompt: str
):
    rpc_url, user_pk = get_env_vars()

    print("Prompt: ", prompt)
    print("User private key: ", user_pk)
    print("RPC URL: ", rpc_url)

    client = EthereumClient(URI(rpc_url))
    web3 = client.w3
    
    user: Account = Account.from_key(user_pk)
    agent: Account = generate_agent_account()

    print("User Address: ", user.address)
    print("Agent Address: ", agent.address)
   
    multicall_addr = deploy_multicall(client, user)
    client.multicall = Multicall(client, multicall_addr)

    _ = send_eth(user, agent.address, 1, web3)
    
    safe_addr, safe = deploy_safe_with_create2(client, user, [user.address, agent.address], 1)

    print("Connected to RPC: ", web3.is_connected())

    print("Before ETH Balance: ", get_eth_balance(safe_addr, web3))

    _ = send_eth(user, safe_addr, 1, web3)
    
    print("After ETH Balance: ", get_eth_balance(safe_addr, web3))
   
    info = safe.retrieve_all_info()

    print("Safe Info: ", info)

if __name__ == '__main__':
    run()
