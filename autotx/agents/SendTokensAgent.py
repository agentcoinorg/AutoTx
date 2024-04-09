from textwrap import dedent
from typing import Annotated, Callable
from autotx.AutoTx import AutoTx
from autotx.autotx_agent import AutoTxAgent
from autotx.autotx_tool import AutoTxTool
from autotx.utils.PreparedTx import PreparedTx
from autotx.utils.ethereum import (
    build_transfer_erc20,
    get_erc20_balance,
)
from autotx.utils.ethereum import load_w3
from autotx.utils.ethereum.build_transfer_eth import build_transfer_eth
from web3.constants import ADDRESS_ZERO
from autotx.utils.ethereum.eth_address import ETHAddress

name = "send-tokens"

system_message = lambda autotx: dedent(f"""
    You are an AI assistant. Assist the user (address: {autotx.manager.address}) in their tasks by fetching balances and preparing transactions to send tokens.
    You are an expert in Ethereum tokens and can help users send tokens and check their balances.
    You use the tools available to assist the user in their tasks. 
    Your job is to only prepare the transactions and the user will take care of executing them.
    NOTE: There is no reason to call get_erc20_balance after calling transfer as the transfers are only prepared and not executed. 
    """
)

class TransferETHTool(AutoTxTool):
    name: str = "prepare_transfer_eth_transaction"
    description: str = dedent(
        """
        Prepares a transfer transaction for given amount in decimals for ETH.
        """
    )

    def build_tool(self, autotx: AutoTx) -> Callable:
        def run(
            amount: Annotated[float, "Amount given by the user to transfer. The function will take care of converting the amount to needed decimals."],
            receiver: Annotated[str, "The receiver's address or ENS domain"]
        ) -> str:
            web3 = load_w3()
      
            receiver_addr = ETHAddress(receiver, web3)
        
            tx = build_transfer_eth(web3, ETHAddress(ADDRESS_ZERO, web3), receiver_addr, amount)
        
            prepared_tx = PreparedTx(f"Transfer {amount} ETH to {str(receiver_addr)}", tx)

            autotx.transactions.append(prepared_tx)

            print(f"Prepared transaction: {prepared_tx.summary}")
            
            return prepared_tx.summary


        return run
        
class TransferERC20Tool(AutoTxTool):
    name: str = "prepare_transfer_erc20_transaction"
    description: str = dedent(
        """
        Prepares a transfer transaction for given amount in decimals for given token.
        """
    )

    def build_tool(self, autotx: AutoTx) -> Callable:
        def run(
            amount: Annotated[float, "Amount given by the user to transfer. The function will take care of converting the amount to needed decimals."],
            receiver: Annotated[str, "The receiver's address or ENS domain"],
            token: Annotated[str, "Symbol of token to transfer"]
        ) -> str:
            token_address = autotx.network.tokens[token.lower()]
            web3 = load_w3()
      
            receiver_addr = ETHAddress(receiver, web3)
        
            tx = build_transfer_erc20(web3, token_address, receiver_addr, amount)
        
            prepared_tx = PreparedTx(f"Transfer {amount} {token} to {str(receiver_addr)}", tx)
        
            autotx.transactions.append(prepared_tx)
        
            print(f"Prepared transaction: {prepared_tx.summary}")
           
            return prepared_tx.summary

        return run
    
class GetETHBalanceTool(AutoTxTool):
    name: str = "get_eth_balance"
    description: str = dedent(
        """
        Check owner balance in ETH
        """
    )

    def build_tool(self, autotx: AutoTx) -> Callable:
        def run(
            owner: Annotated[str, "The owner's address or ENS domain"]
        ) -> float:
            web3 = load_w3()
            
            owner_addr = ETHAddress(owner, web3)

            eth_balance = web3.eth.get_balance(owner_addr.hex)

            print(f"Fetching ETH balance for {str(owner_addr)}: {eth_balance / 10 ** 18} ETH")
          
            return eth_balance / 10 ** 18

        return run
    
class GetERC20BalanceTool(AutoTxTool):
    name: str = "get_erc20_balance"
    description: str = dedent(
        """
        Check owner balance in ERC20 token
        """
    )

    def build_tool(self, autotx: AutoTx) -> Callable:
        def run(
            token: Annotated[str, "Token symbol of erc20"],
            owner: Annotated[str, "The token owner's address or ENS domain"]
        ) -> float:
            web3 = load_w3()
            token_address = ETHAddress(autotx.network.tokens[token.lower()], web3)
            owner_addr = ETHAddress(owner, web3)

            balance = get_erc20_balance(web3, token_address, owner_addr)

            print(f"Fetching {token} balance for {str(owner_addr)}: {balance} {token}")
            
            return balance

        return run

class SendTokensAgent(AutoTxAgent):
    name = name
    system_message = system_message
    tools = [
        TransferETHTool(),
        TransferERC20Tool(),
        GetETHBalanceTool(),
        GetERC20BalanceTool()
    ]