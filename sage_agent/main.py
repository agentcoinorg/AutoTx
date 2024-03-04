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
    sage.run(prompt)

if __name__ == '__main__':
    run()
