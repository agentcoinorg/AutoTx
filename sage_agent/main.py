from dotenv import load_dotenv
load_dotenv()

import click
from textwrap import dedent
from sage_agent.agents.erc20 import Erc20Agent
from sage_agent.agents.safe import SafeAgent
from sage_agent.agents.uniswap import UniswapAgent
from sage_agent.sage import Sage
from sage_agent.patch import patch_langchain
from sage_agent.utils.ethereum import deploy_mock_erc20
from sage_agent.utils.ethereum.SafeManager import SafeManager
from sage_agent.utils.ethereum.send_eth import send_eth
from sage_agent.utils.ethereum.transfer_erc20 import transfer_erc20
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

    dai_balance = manager.balance_of("0x6B175474E89094C44Da98b954EedeAC495271d0F")
    usdc_balance = manager.balance_of("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    eth_balance = manager.balance_of(None)
    wbtc_balance = manager.balance_of("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")
    print(
        dedent(
            f"""
            DAI Balance: {dai_balance / 10 ** 18}
            USDC Balance: {usdc_balance / 10 ** 6}
            WBTC Balance: {wbtc_balance / 10 ** 8}
            ETH Balance: {eth_balance / 10 ** 18}
            """
        )
    )

    # # Send 0.01 ETH to the agent, so it can execute transactions
    _ = send_eth(user, agent.address, int(0.01 * 10**18), web3)

    # Send 5 ETH to the safe, so it can execute transactions
    # _ = send_eth(user, manager.address, int(5 * 10**18), web3)

    # Send 100 TestToken to the safe, so it can use it
    # transfer_tx = transfer_erc20(
    #     web3, token_address, user, manager.address, int(100 * 10**18)
    # )
    # manager.wait(transfer_tx)

    erc20_agent = Erc20Agent([token_address])
    safe_agent = SafeAgent(manager, agent)
    uniswap_agent = UniswapAgent(client, manager.address)

    sage = Sage([erc20_agent, safe_agent, uniswap_agent], None)

    sage.run(prompt)

    dai_balance = manager.balance_of("0x6B175474E89094C44Da98b954EedeAC495271d0F")
    usdc_balance = manager.balance_of("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    eth_balance = manager.balance_of(None)
    wbtc_balance = manager.balance_of("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")

    print(
        dedent(
            f"""
            DAI Balance: {dai_balance / 10 ** 18}
            USDC Balance: {usdc_balance / 10 ** 6}
            WBTC Balance: {wbtc_balance / 10 ** 8}
            ETH Balance: {eth_balance / 10 ** 18}
            """
        )
    )


if __name__ == "__main__":
    run()
