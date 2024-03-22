from textwrap import dedent
from typing import Callable
from crewai import Agent
from pydantic import ConfigDict, Field
from autotx.AutoTx import AutoTx
from autotx.utils.agents_config import AgentConfig, agents_config
from autotx.utils.ethereum import (
    build_transfer_erc20,
    get_erc20_balance,
)
from autotx.utils.ethereum import load_w3
from autotx.utils.ethereum.build_transfer_eth import build_transfer_eth
from autotx.utils.llm import open_ai_llm
from autotx.utils.ethereum.config import contracts_config
from web3.constants import ADDRESS_ZERO
from crewai_tools import BaseTool

class TransferERC20TokenTool(BaseTool):
    name: str = "Transfer ERC20 token"
    description: str = dedent(
        """
        Prepares a transfer transaction for given amount in decimals for given token

        Args:
            amount (float): Amount given by the user to transfer. The function will take
            care of converting the amount to needed decimals.
            reciever (str): The receiver's address or ENS domain
            token (str): Symbol of token to transfer
        Returns:
            Message to confirm that transaction has been prepared
        """
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)
    autotx: AutoTx = Field(None)

    def __init__(self, autotx: AutoTx):
        super().__init__()
        self.autotx = autotx

    def _run(
        self, amount: float, reciever: str, token: str
    ) -> str:
        tokens = contracts_config["erc20"]
        token_address = tokens[token.lower()]
        tx = build_transfer_erc20(load_w3(), token_address, reciever, amount)

        self.autotx.transactions.append(tx)

        return f"Transaction to send {amount} {token} has been prepared"

class TransferETHTool(BaseTool):
    name: str = "Transfer ETH"
    description: str = dedent(
        """
        Prepares a transfer transaction for given amount in decimals for ETH

        Args:
            amount (float): Amount given by the user to transfer. The function will take
            care of converting the amount to needed decimals.
            reciever (str): The receiver's address or ENS domain
        Returns:
            Message to confirm that transaction has been prepared
        """
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)
    autotx: AutoTx = Field(None)

    def __init__(self, autotx: AutoTx):
        super().__init__()
        self.autotx = autotx

    def _run(
        self, amount: float, reciever: str
    ) -> str:
        tx = build_transfer_eth(load_w3(), ADDRESS_ZERO, reciever, amount)

        self.autotx.transactions.append(tx)

        return f"Transaction to send {amount} ETH has been prepared"

class GetBalanceTool(BaseTool):
    name: str = "Transfer ETH"
    description: str = dedent(
        """
        Check owner balance in ERC20 token

        :param token: str, token symbol of erc20
        :param owner: str, the token owner's address or ENS domain

        :result balance: int, the balance of owner in erc20 contract
        """
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)
    autotx: AutoTx = Field(None)

    def __init__(self, autotx: AutoTx):
        super().__init__()
        self.autotx = autotx

    def _run(
        self, token: str, owner: str
    ) -> int:
        tokens = contracts_config["erc20"]
        token_address = tokens[token.lower()]
        
        return get_erc20_balance(load_w3(), token_address, owner)

class SendTokensAgent(Agent):
    name: str

    def __init__(self, autotx: AutoTx):
        name = "send-tokens"
        config: AgentConfig = agents_config[name].model_dump()
        super().__init__(
            **config,
            tools=[
                TransferERC20TokenTool(autotx),
                TransferETHTool(autotx),
                GetBalanceTool(autotx)
            ],
            llm=open_ai_llm,
            verbose=True,
            allow_delegation=False,
            name=name,
        )

def build_agent_factory() -> Callable[[AutoTx], Agent]:
    def agent_factory(autotx: AutoTx) -> SendTokensAgent:
        return SendTokensAgent(autotx)
    return agent_factory
