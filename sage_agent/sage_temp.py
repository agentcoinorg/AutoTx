from dataclasses import dataclass
from crewai import Agent
# from langchain_openai import ChatOpenAI
# from agents.erc20 import Erc20Agent
# from tools.ethereum import EthereumTools
from sage_agent.tools.uniswap import UniswapTools
from sage_agent.tools.lifi import BridgeTools
from sage_agent.tools.safe import SafeTools
from sage_agent.tools.erc20 import Erc20Tools
from sage_agent.utils.llm import open_ai_llm

@dataclass(kw_only=True)
class Config:
    verbose: bool

class SageAgent:
    def erc_20_agent():
        return Agent(
            role="ERC20 Specialist",
            goal="Streamline ERC20 token interactions for efficient and error-free operations.",
            backstory="""
Crafted from the need to navigate the ERC20 token standards,
this agent automates and simplifies token transfers, approvals,
and balance queries, supporting high-stakes DeFi operations.
            """,
            tools=[
                Erc20Tools.encode,
                Erc20Tools.get_balance,
                Erc20Tools.get_information,
            ],
            llm=open_ai_llm,
            verbose=True,
            allow_delegation=False,
        )

    def safe_agent():
        return Agent(
            role="Gnosis Safe Smart Wallet Assistant",
            goal="Securely manage multisig transactions and configurations on Gnosis Safe contracts.",
            backstory="""
A seasoned blockchain security expert, designed to ensure flawless execution of multisig
transactions and optimal configurations for DeFi operations security.
        """,
            tools=[
                SafeTools.create_transaction,
                SafeTools.execute_transaction,
                SafeTools.sign_transaction,
            ],
            llm=open_ai_llm,
            verbose=True,
            allow_delegation=True,
        )

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


# def sage_agent():
#     return Agent(
#         role="Ethereum Assistant",
#         goal="Handle complex interactions with Ethereum blockchain",
#         backstory="""
# Tasked with crafting transactions, encoding function calls, and mastering interactions  with contracts in Ethereum,
# it exists to streamline and innovate within Ethereum's decentralized ecosystem
# """,
#         tools=[
#             EthereumTools.send_transaction,
#             Erc20Tools.encode,
#             Erc20Tools.get_balance,
#             Erc20Tools.get_information,
#             BridgeTools.get_quote,
#             SafeTools.create_transaction,
#             UniswapTools.encode_swap,
#             UniswapTools.query_pools,
#         ],
#         llm=llm,
#         verbose=True,
#     )
