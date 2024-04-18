from decimal import Decimal
from textwrap import dedent
from typing import Annotated, Callable
from autotx.AutoTx import AutoTx
from autotx.autotx_agent import AutoTxAgent
from autotx.autotx_tool import AutoTxTool
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.lifi.swap import build_swap_transaction
from autotx.utils.ethereum.networks import NetworkInfo

name = "swap-tokens"

system_message = lambda autotx: dedent(f"""
    You are an expert at buying and selling tokens. Assist the user (address: {autotx.manager.address}) in their task of swapping tokens.
    ONLY focus on the buy and sell (swap) aspect of the user's goal and let other agents handle other tasks.
    You use the tools available to assist the user in their tasks.
    Note a balance of a token is not required to perform a swap, if there is an earlier prepared transaction that will provide the token.
    Below are examples, NOTE these are only examples and in practice you need to call the prepare_swap_transaction tool with the correct arguments.
    Example 1:
    User: Send 0.1 ETH to vitalik.eth and then swap ETH to 5 USDC
    ...
    Other agent messages
    ...
    Call prepare_swap_transaction with args:
    {{
        "token_to_sell": "ETH",
        "token_to_buy": "5 USDC"
    }}

    Example 2:
    User: Swap ETH to 5 USDC, then swap that USDC for 6 UNI
    Call prepare_swap_transaction with args:
    {{
        "token_to_sell": "ETH",
        "token_to_buy": "5 USDC"
    }}
    and then
    Call prepare_swap_transaction with args:
    {{
        "token_to_sell": "USDC",
        "token_to_buy": "6 UNI"
    }}

    Example 3:
    User: Buy 10 USDC with ETH and then buy UNI with 5 USDC
    Call prepare_swap_transaction with args:
    {{
        "token_to_sell": "ETH",
        "token_to_buy": "10 USDC"
    }}
    and then
    Call prepare_swap_transaction with args:
    {{
        "token_to_sell": "5 USDC",
        "token_to_buy": "UNI"
    }}
    
    Example 4 (Mistake):
    User: Swap ETH for 5 USDC, then swap that USDC for 6 UNI
    Call prepare_swap_transaction with args:
    {{
        "token_to_sell": "ETH",
        "token_to_buy": "5 USDC"
    }}
    and then
    Call prepare_swap_transaction with args:
    {{
        "token_to_sell": "5 USDC",
        "token_to_buy": "6 UNI"
    }}
    Invalid input. Only one token amount should be provided. IMPORTANT: Take another look at the user's goal, and try again.
    To fix the error run:
    Call prepare_swap_transaction with args:
    {{
        "token_to_sell": "USDC",
        "token_to_buy": "6 UNI"
    }}
    Above are examples, NOTE these are only examples and in practice you need to call the prepare_swap_transaction tool with the correct arguments.
    Take extra care in ensuring you have to right amount next to the token symbol.
    Only call tools, do not respond with JSON.
    """
)

def get_tokens_address(token_in: str, token_out: str, network_info: NetworkInfo) -> tuple[str, str]:
    token_in = token_in.lower()
    token_out = token_out.lower()

    if token_in not in network_info.tokens:
        raise Exception(f"Token {token_in} is not supported in network {network_info.chain_id.name.lower()}")

    if token_out not in network_info.tokens:
        raise Exception(f"Token {token_out} is not supported in network {network_info.chain_id.name.lower()}")

    return (network_info.tokens[token_in], network_info.tokens[token_out])

class SwapTool(AutoTxTool):
    name: str = "prepare_swap_transaction"
    description: str = dedent(
        """
        Prepares a swap transaction for given amount in decimals for given token. Swap should only include the amount for one of the tokens, the other token amount will be calculated automatically.
        """
    )

    def build_tool(self, autotx: AutoTx) -> Callable[[str, str], str]:
        def run(
            token_to_sell: Annotated[str, "Token to sell. E.g. '10 USDC' or just 'USDC'"],
            token_to_buy: Annotated[str, "Token to buy. E.g. '10 USDC' or just 'USDC'"],
        ) -> str:
            sell_parts = token_to_sell.split(" ")
            buy_parts = token_to_buy.split(" ")

            if len(sell_parts) == 2 and len(buy_parts) == 2:
                return "Invalid input. Only one token amount should be provided. IMPORTANT: Take another look at the user's goal, and try again."
            
            if len(sell_parts) < 2 and len(buy_parts) < 2:
                return "Invalid input. Token amount is missing.\n"

            token_symbol_to_sell = sell_parts[1] if len(sell_parts) == 2 else sell_parts[0]
            token_symbol_to_buy = buy_parts[1] if len(buy_parts) == 2 else buy_parts[0]

            exact_amount = sell_parts[0] if len(sell_parts) == 2 else buy_parts[0]
            amount_symbol = token_symbol_to_sell if len(sell_parts) == 2 else token_symbol_to_buy

            token_in = token_symbol_to_sell.lower()
            token_out = token_symbol_to_buy.lower()
            is_exact_input = amount_symbol == token_symbol_to_sell 

            (token_in_address, token_out_address) = get_tokens_address(
                token_in, token_out, autotx.network
            )

            swap_transactions = build_swap_transaction(
                autotx.manager.client,
                Decimal(exact_amount),
                ETHAddress(token_in_address),
                ETHAddress(token_out_address),
                autotx.manager.address,
                is_exact_input,
                autotx.network.chain_id
            )
            autotx.transactions.extend(swap_transactions)

            summary = "".join(
                f"Prepared transaction: {swap_transaction.summary}\n"
                for swap_transaction in swap_transactions
            )

            print(summary)
            return summary

        return run

class SwapTokensAgent(AutoTxAgent):
    name = name
    system_message = system_message
    tools = [
        SwapTool()
    ]
