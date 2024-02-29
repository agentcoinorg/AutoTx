from crewai import Agent
from langchain_openai import ChatOpenAI
from tools.uniswap import UniswapTools
from tools.ethereum import EthereumTools
from tools.lifi import BridgeTools
from tools.safe import SafeTools
from tools.erc20 import Erc20Tools

llm = ChatOpenAI(model="gpt-4-turbo-preview")  # type: ignore


class SageAgents:
    def __init__(self):
        self.OpenAIGPT35 = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
        self.OpenAIGPT4 = ChatOpenAI(model="gpt-4-turbo-preview")

#     def ethereum_agent(self):
#         return Agent(
#             role="Senior Ethereum Blockchain Developer",
#             goal="Give guidance to interact with Ethereum",
#             backstory="""
# As a Senior Ethereum Blockchain Developer, the 
# primary role is to provide expert guidance and support to its team, enabling them
# to execute complex interactions with the Ethereum blockchain efficiently and effectively.
# """,
#             tools=[
#                 EthereumTools.send_transaction,
#             ],
#             llm=self.OpenAIGPT4,
#             verbose=True,
#             allow_delegation=True,
#         )

    def erc_20_agent(self):
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
            llm=self.OpenAIGPT4,
            verbose=True,
            allow_delegation=False,
        )

    def safe_agent(self):
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
            llm=self.OpenAIGPT4,
            verbose=True,
            allow_delegation=True,
        )

    def bridge_agent(self):
        return Agent(
            role="Ethereum Ecosystem Multichain Specialist",
            goal="Handle the creation of transactions that interact with bridges",
            backstory="""
Multichain Ecosystem Maxi. You know how to interact with multiple L1 & L2 
through bridges; you're proefficient in getting quotes for multichain 
interactions and return the correct calldata
""",
            tools=[BridgeTools.get_quote],
            llm=self.OpenAIGPT4,
            verbose=True,
            allow_delegation=False,
        )

    def uniswap_agent(self):
        return Agent(
            role="Uniswap Protocol Interactor",
            goal="Perform token swaps, manage liquidity, and query pool statistics on the Uniswap protocol",
            backstory="""
            An autonomous agent skilled in Ethereum blockchain interactions,
            specifically tailored for the Uniswap V3 protocol.
            """,
            verbose=True,
            tools=[UniswapTools.encode_swap, UniswapTools.query_pools],
            llm=self.OpenAIGPT4
        )


def sage_agent():
    return Agent(
        role="Ethereum Assistant",
        goal="Handle complex interactions with Ethereum blockchain",
        backstory="""
Tasked with crafting transactions, encoding function calls, and mastering interactions  with contracts in Ethereum,
it exists to streamline and innovate within Ethereum's decentralized ecosystem
""",
        tools=[
            EthereumTools.send_transaction,
            Erc20Tools.encode,
            Erc20Tools.get_balance,
            Erc20Tools.get_information,
            BridgeTools.get_quote,
            SafeTools.create_transaction,
            UniswapTools.encode_swap,
            UniswapTools.query_pools,
        ],
        llm=llm,
        verbose=True,
    )
