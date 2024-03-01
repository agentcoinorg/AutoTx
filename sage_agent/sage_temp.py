from crewai import Agent
# from langchain_openai import ChatOpenAI
# from agents.erc20 import Erc20Agent
# from tools.ethereum import EthereumTools
from sage_agent.tools.uniswap import UniswapTools
from sage_agent.tools.lifi import BridgeTools
from sage_agent.utils.llm import open_ai_llm


class SageAgent:
    def bridge_agent():
        return Agent(
            role="Ethereum Ecosystem Multichain Specialist",
            goal="Handle the creation of transactions that interact with bridges",
            backstory="""
Multichain Ecosystem Maxi. You know how to interact with multiple L1 & L2 
through bridges; you're proefficient in getting quotes for multichain 
interactions and return the correct calldata
""",
            tools=[BridgeTools.get_quote],
            llm=open_ai_llm,
            verbose=True,
            allow_delegation=False,
        )

    def uniswap_agent():
        return Agent(
            role="Uniswap Protocol Interactor",
            goal="Perform token swaps, manage liquidity, and query pool statistics on the Uniswap protocol",
            backstory="""
            An autonomous agent skilled in Ethereum blockchain interactions,
            specifically tailored for the Uniswap V3 protocol.
            """,
            verbose=True,
            tools=[UniswapTools.encode_swap, UniswapTools.query_pools],
            llm=open_ai_llm
        )

