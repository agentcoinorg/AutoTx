from textwrap import dedent
from typing import Annotated, Callable

from web3 import Web3
from autotx.AutoTx import AutoTx
from autotx.autotx_agent import AutoTxAgent
from autotx.autotx_tool import AutoTxTool
from autotx.utils.PreparedTx import PreparedTx
from autotx.utils.ethereum import (
    build_transfer_erc20,
    get_erc20_balance,
)
from autotx.utils.ethereum import load_w3
from autotx.utils.ethereum.build_transfer_native import build_transfer_native
from web3.constants import ADDRESS_ZERO
from autotx.utils.ethereum.constants import NATIVE_TOKEN_ADDRESS
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.get_native_balance import get_native_balance

name = "send-tokens"

system_message = lambda autotx: dedent(f"""
    You are an expert in Ethereum tokens (native and erc20) and can assist the user (address: {autotx.manager.address}) in their tasks by fetching balances and preparing transactions to send tokens.
    ONLY focus on the sending and balance aspect of the user's goal and let other agents handle other tasks.
    You use the tools available to assist the user in their tasks. 
    Your job is to only prepare the transactions by calling the prepare_transfer_transaction tool and the user will take care of executing them.
    NOTE: There is no reason to call get_token_balance after calling prepare_transfer_transaction as the transfers are only prepared and not executed. 
    Do not just respond with JSON, instead call the tools with the correct arguments.
    """
)

class TransferTokenTool(AutoTxTool):
    name: str = "prepare_transfer_transaction"
    description: str = dedent(
        """
        Prepares a transfer transaction for given amount in decimals for a token
        """
    )

    def build_tool(self, autotx: AutoTx) -> Callable[[float, str, str], str]:
        def run(
            amount: Annotated[float, "Amount given by the user to transfer. The function will take care of converting the amount to needed decimals."],
            receiver: Annotated[str, "The receiver's address or ENS domain"],
            token: Annotated[str, "Symbol of token to transfer"]
        ) -> str:
            amount = float(amount)

            web3 = load_w3()
            receiver_addr = ETHAddress(receiver, web3)
            token_address = ETHAddress(autotx.network.tokens[token.lower()], web3)

            prepared_tx: PreparedTx | None = None

            if token_address.hex == NATIVE_TOKEN_ADDRESS:
                tx = build_transfer_native(web3, ETHAddress(ADDRESS_ZERO, web3), receiver_addr, amount)
            else:
                tx = build_transfer_erc20(web3, token_address, receiver_addr, amount)

            prepared_tx = PreparedTx(f"Transfer {amount} {token} to {str(receiver_addr)}", tx)

            autotx.transactions.append(prepared_tx)
            
            print(f"Prepared transaction: {prepared_tx.summary}")
            
            return prepared_tx.summary

        return run

class GetTokenBalanceTool(AutoTxTool):
    name: str = "get_token_balance"
    description: str = dedent(
        """
        Check owner balance of token
        """
    )

    def build_tool(self, autotx: AutoTx) -> Callable[[str, str], float]:
        def run(
            token: Annotated[str, "Token symbol of erc20"],
            owner: Annotated[str, "The token owner's address or ENS domain"]
        ) -> float:
            web3 = load_w3()
            owner_addr = ETHAddress(owner, web3)
            token_address = ETHAddress(autotx.network.tokens[token.lower()], web3)
            
            balance: float = 0

            if token_address.hex == NATIVE_TOKEN_ADDRESS:
                balance = get_native_balance(web3, owner_addr)
            else:
                balance = get_erc20_balance(web3, token_address, owner_addr)

            print(f"Fetching {token} balance for {str(owner_addr)}: {balance} {token}")
            
            return balance

        return run
    
class SendTokensAgent(AutoTxAgent):
    name = name
    system_message = system_message
    tools = [
        TransferTokenTool(),
        GetTokenBalanceTool(),
    ]