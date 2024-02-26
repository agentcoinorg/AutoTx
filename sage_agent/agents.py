from crewai import Agent
from langchain_openai import ChatOpenAI
from tools.ethereum import EthereumTools
from tools.lifi import BridgeTools
from tools.safe import SafeTools
from tools.erc20 import Erc20Tools

llm = ChatOpenAI(model="gpt-4-1106-preview")  # type: ignore


class SageAgents:
    def __init__(self):
        self.OpenAIGPT35 = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
        self.OpenAIGPT4 = ChatOpenAI(model="gpt-4-turbo-preview")

    def ethereum_agent(self):
        return Agent(
            role="Senior Ethereum Blockchain Developer",
            goal="Create complex transaction in ethereum",
            backstory="""
You are obssesed with good quality so you pay a lot of attention to details
when it comes to execute a goal. You make sure that before taking any step,
all necessary information has been gathered; using your team to succesfully execute the task.

Before interacting with any ERC20 transaction you must guarantee that tokens are defined
            """,
            tools=[
                EthereumTools.send_transaction
            ],
            llm=self.OpenAIGPT4,
            verbose=True,
            allow_delegation=True,
        )

    def erc_20_agent(self):
        return Agent(
            role="ERC 20 Smart Contracts Assistant",
            goal="Get all needed information from ERC20 Tokens",
            backstory="""
You're proefficient when it comes to interact with ERC 20 tokens,
Your main goal is to provide the correct tooling to interact with those,
by gathering information and encoding transactions
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
            goal="Interact with Safe Smart Contracts",
            backstory="""
You are a developer with strong knowledge when it comes to interact with Safe Smart Contracts.
You know how to orchestrate complex interactions with the Safe Protocol.
        """,
            tools=[
                SafeTools.create_transaction,
                SafeTools.execute_transaction,
                SafeTools.sign_transaction,
                # SafeTools.create_multisend
            ],
            llm=self.OpenAIGPT4,
            verbose=True,
            allow_delegation=False,
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