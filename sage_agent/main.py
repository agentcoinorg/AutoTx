import click
from dotenv import load_dotenv
from sage_agent.agents.erc20 import Erc20Agent
from sage_agent.agents.safe import SafeAgent
from sage_agent.agents.uniswap import UniswapAgent
from sage_agent.sage import Sage

load_dotenv()

@click.command()
@click.option('--prompt',
    prompt='Prompt',
    required=True,
    help='Prompt'
)
def run(prompt: str):
    erc20_agent = Erc20Agent()
    safe_agent = SafeAgent()
    uniswap_agent = UniswapAgent()
    sage = Sage([erc20_agent, safe_agent, uniswap_agent], None)
    sage.run("Create and sign a transaction in my safe to send 0.4 Cool Token (token address: 0x57c94aa4a136506d3b88d84473bf3dc77f5b51da) to 0x1816d5Dd8a4081D64bd1518532440125438c79A6")

if __name__ == '__main__':
    run()
