from textwrap import dedent
from typing import Callable
from crewai import Agent
from web3 import Web3
from autotx.AutoTx import AutoTx
from autotx.auto_tx_agent import AutoTxAgent
from autotx.auto_tx_tool import AutoTxTool
from autotx.utils.PreparedTx import PreparedTx
from autotx.utils.ethereum import (
    build_transfer_erc20,
    get_address,
    get_erc20_balance,
)
from autotx.utils.ethereum import load_w3
from autotx.utils.ethereum.build_transfer_eth import build_transfer_eth
from autotx.utils.ethereum.config import contracts_config
from web3.constants import ADDRESS_ZERO

class TransferERC20TokenTool(AutoTxTool):
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

    def _run(
        self, amount: float, reciever: str, token: str
    ) -> str:
        tokens = contracts_config["erc20"]
        token_address = tokens[token.lower()]
        web3 = load_w3()

        if not Web3.is_address(reciever) and not reciever.endswith(".eth"):
            raise ValueError("Invalid receiver address")

        tx = build_transfer_erc20(web3, token_address, reciever, amount)

        related_addr = f"({get_address(web3, reciever)})" if reciever.endswith(".eth") else ""
        self.autotx.transactions.append(PreparedTx(f"Transfer {amount} {token} to {reciever}{related_addr}", tx))

        return f"Transaction to send {amount} {token} has been prepared"

class TransferETHTool(AutoTxTool):
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

    def _run(
        self, amount: float, reciever: str
    ) -> str:
        web3 = load_w3()
      
        if not Web3.is_address(reciever) and not reciever.endswith(".eth"):
            raise ValueError("Invalid receiver address")
    
        tx = build_transfer_eth(web3, ADDRESS_ZERO, reciever, amount)
      
        related_addr = f"({get_address(web3, reciever)})" if reciever.endswith(".eth") else ""
        self.autotx.transactions.append(PreparedTx(f"Transfer {amount} ETH to {reciever}{related_addr}", tx))

        return f"Transaction to send {amount} ETH has been prepared"

class GetBalanceTool(AutoTxTool):
    name: str = "Get balance"
    description: str = dedent(
        """
        Check owner balance in ERC20 token

        :param token: str, token symbol of erc20
        :param owner: str, the token owner's address or ENS domain

        :result balance: int, the balance of owner in erc20 contract
        """
    )

    def _run(
        self, token: str, owner: str
    ) -> int:
        tokens = contracts_config["erc20"]
        token_address = tokens[token.lower()]
        
        return get_erc20_balance(load_w3(), token_address, owner)

class SendTokensAgent(AutoTxAgent):
    def __init__(self, autotx: AutoTx):
        super().__init__(
            name="send-tokens",
            role="Ethereum token specialist",
            goal="Streamline ERC20 token interactions for efficient and error-free operations.",
            backstory="Crafted from the need to navigate the ERC20 token standards, this agent automates and simplifies token transfers, approvals, and balance queries, supporting high-stakes DeFi operations.",
            tools=[
                TransferERC20TokenTool(autotx),
                TransferETHTool(autotx),
                GetBalanceTool(autotx)
            ],
        )

def build_agent_factory() -> Callable[[AutoTx], Agent]:
    def agent_factory(autotx: AutoTx) -> SendTokensAgent:
        return SendTokensAgent(autotx)
    return agent_factory
