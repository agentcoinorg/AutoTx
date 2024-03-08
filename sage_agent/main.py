import click
from dotenv import load_dotenv
from eth_account import Account
from sage_agent. get_env_vars import get_env_vars
from sage_agent.agents.erc20 import Erc20Agent
from sage_agent.agents.safe import SafeAgent
from sage_agent.agents.uniswap import UniswapAgent
from sage_agent.sage import Sage
from sage_agent.patch import patch_langchain
from sage_agent.utils.ethereum import deploy_mock_erc20, load_w3
from sage_agent.utils.ethereum.SafeManager import SafeManager
from sage_agent.utils.ethereum.build_transfer_erc20 import build_transfer_erc20
from sage_agent.utils.ethereum.generate_agent_account import generate_agent_account
from sage_agent.utils.ethereum.send_eth import send_eth
from sage_agent.utils.ethereum.transfer_erc20 import transfer_erc20

load_dotenv()
patch_langchain()

@click.command()
@click.option('--prompt',
    prompt='Prompt',
    required=True,
    help='Prompt'
)
def run(prompt: str):
    rpc_url, user_pk = get_env_vars()
    web3 = load_w3()

    user: Account = Account.from_key(user_pk)
    agent: Account = generate_agent_account()
    random_address = Account.create().address
    token_address = deploy_mock_erc20(web3, user)

    prompt = f"Send 0.4 TT to {random_address} through my safe"
    print(prompt)

    manager = SafeManager.deploy_safe(rpc_url, user, agent, [user.address, agent.address], 1)

    # Send 0.01 ETH to the agent, so it can execute transactions
    _ = send_eth(user, agent.address, int(0.01 * 10 ** 18), web3)
    # Send 100 TestToken to the safe, so it can use it
    transfer_tx = transfer_erc20(web3, token_address, user, manager.address, int(100 * 10**18))
    manager.wait(transfer_tx)

    tx = manager.send_txs([
        build_transfer_erc20(web3, token_address, random_address, int(0.4 * 10**18))
    ])
    manager.wait(tx)

    erc20_agent = Erc20Agent([token_address])
    safe_agent = SafeAgent(manager, agent)
    uniswap_agent = UniswapAgent()
    sage = Sage([erc20_agent, safe_agent, uniswap_agent], None)
    sage.run(prompt)

if __name__ == '__main__':
    run()
