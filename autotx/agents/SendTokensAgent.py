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
    get_erc20_balance,
)
from autotx.utils.ethereum import load_w3
from autotx.utils.ethereum.build_transfer_eth import build_transfer_eth
from web3.constants import ADDRESS_ZERO

from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.erc20_abi import ERC20_ABI

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
        tokens = self.autotx.network.tokens
        token_address = tokens[token.lower()]
        web3 = load_w3()

        reciever_addr = ETHAddress(reciever, web3)
        
        tx = build_transfer_erc20(web3, token_address, reciever_addr, amount)

        self.autotx.transactions.append(PreparedTx(f"Transfer {amount} {token} to {str(reciever_addr)}", tx))

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
      
        reciever_addr = ETHAddress(reciever, web3)
    
        tx = build_transfer_eth(web3, ETHAddress(ADDRESS_ZERO, web3), reciever_addr, amount)
      
        self.autotx.transactions.append(PreparedTx(f"Transfer {amount} ETH to {str(reciever_addr)}", tx))

        return f"Transaction to send {amount} ETH has been prepared"

class GetERC20BalanceTool(AutoTxTool):
    name: str = "Get ERC20 balance"
    description: str = dedent(
        """
        Check owner balance in ERC20 token

        :param token: str, token symbol of erc20
        :param owner: str, the token owner's address or ENS domain

        :result balance: float, the balance of owner in erc20 contract
        """
    )

    def _run(
        self, token: str, owner: str
    ) -> float:
        web3 = load_w3()
        tokens = self.autotx.network.tokens
        token_address = ETHAddress(tokens[token.lower()], web3)
        owner_addr = ETHAddress(owner, web3)
        
        return get_erc20_balance(web3, token_address, owner_addr)

class GetETHBalanceTool(AutoTxTool):
    name: str = "Get ETH balance"
    description: str = dedent(
        """
        Check owner balance in ETH

        :param owner: str, the owner's address or ENS domain

        :result balance: float, the balance of owner in ETH
        """
    )

    def _run(
        self, owner: str
    ) -> float:
        web3 = load_w3()
        owner_addr = ETHAddress(owner, web3)

        eth_balance = web3.eth.get_balance(owner_addr.hex)

        return eth_balance / 10 ** 18

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
                GetERC20BalanceTool(autotx),
                GetETHBalanceTool(autotx),
            ],
        )

def build_agent_factory() -> Callable[[AutoTx], Agent]:
    def agent_factory(autotx: AutoTx) -> SendTokensAgent:
        return SendTokensAgent(autotx)
    return agent_factory
