from textwrap import dedent
from typing import Annotated, Any, Callable, cast

from web3 import Web3
from autotx import models
from autotx.AutoTx import AutoTx
from autotx.autotx_agent import AutoTxAgent
from autotx.autotx_tool import AutoTxTool
from autotx.utils.ethereum import (
    build_transfer_erc20,
    get_erc20_balance,
)
from autotx.utils.ethereum.build_transfer_native import build_transfer_native
from web3.constants import ADDRESS_ZERO
from autotx.utils.ethereum.constants import NATIVE_TOKEN_ADDRESS
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.get_native_balance import get_native_balance
from web3.types import TxParams

name = "send-tokens"

system_message = lambda autotx: dedent(f"""
    You are an expert in Ethereum tokens (native and erc20) and can assist the user in their tasks by fetching balances and preparing transactions to send tokens.
    You are in a group of agents that will help the user achieve their goal.
    ONLY focus on the sending and balance aspect of the user's goal and let other agents handle other tasks.
    You use the tools available to assist the user in their tasks. 
    Your job is to only prepare the transactions by calling the prepare_transfer_transaction tool and the user will take care of executing them.
    NOTE: There is no reason to call get_token_balance after calling prepare_transfer_transaction as the transfers are only prepared and not executed. 
    NOTE: A balance of a token is not required to perform a send, if there is an earlier prepared transaction that will provide the token.
    NEVER ask the user questions.
    
    Example 1:
    User: Send 0.1 ETH to vitalik.eth and then swap ETH to 5 USDC
    Call prepare_transfer_transaction with args:
    {{
        "amount": 0.1,
        "receiver": "vitalik.eth",
        "token": "ETH"
    }}

    Example 2:
    User: Send 53 UNI to 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
    Call prepare_transfer_transaction with args:
    {{
        "amount": 53,
        "receiver": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
        "token": "UNI"
    }}

    Example 3:
    User: Send 10 USDC to 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 then buy 5 UNI with ETH and send 40 WBTC to 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
    Call prepare_transfer_transaction with args:
    {{
        "amount": 10,
        "receiver": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
        "token": "USDC"
    }}
    NOTE: the second transfer was not prepared because it's waiting for the swap transaction to be prepared first.

    Above are examples, NOTE these are only examples and in practice you need to call the tools with the correct arguments. NEVER respond with JSON.
    Take extra care in the order of transactions to prepare.
    IF a prepared swap transaction will provide the token needed for a transfer, you DO NOT need to call the get_token_balance tool.
    """
)

description = dedent(
    f"""
    {name} is an AI assistant that's an expert in Ethereum tokens (native and erc20).
    The agent can fetch token balances and prepare transactions to send tokens.
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

            receiver_addr = ETHAddress(receiver)
            token_address = ETHAddress(autotx.network.tokens[token.lower()])

            tx: TxParams

            if token_address.hex == NATIVE_TOKEN_ADDRESS:
                tx = build_transfer_native(autotx.web3, ETHAddress(ADDRESS_ZERO), receiver_addr, amount)
            else:
                tx = build_transfer_erc20(autotx.web3, token_address, receiver_addr, amount)

            prepared_tx = models.SendTransaction.create(
                token_symbol=token,
                token_address=str(token_address),
                amount=amount,
                receiver=str(receiver_addr),
                params=cast(dict[str, Any], tx),
            )

            autotx.add_transactions([prepared_tx])
            
            autotx.notify_user(f"Prepared transaction: {prepared_tx.summary}")
            
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
            web3 = autotx.web3
            owner_addr = ETHAddress(owner)
            token_address = ETHAddress(autotx.network.tokens[token.lower()])
            
            balance: float = 0

            if token_address.hex == NATIVE_TOKEN_ADDRESS:
                balance = get_native_balance(web3, owner_addr)
            else:
                balance = get_erc20_balance(web3, token_address, owner_addr)

            autotx.notify_user(f"Fetching {token} balance for {str(owner_addr)}: {balance} {token}")
            
            return balance

        return run
    
class SendTokensAgent(AutoTxAgent):
    name = name
    system_message = system_message
    description = description
    tools = [
        TransferTokenTool(),
        GetTokenBalanceTool(),
    ]