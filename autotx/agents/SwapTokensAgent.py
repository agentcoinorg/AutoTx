from decimal import Decimal
from textwrap import dedent
from typing import Annotated, Callable
from autotx.AutoTx import AutoTx
from autotx.autotx_agent import AutoTxAgent
from autotx.autotx_tool import AutoTxTool
from autotx.utils.ethereum.networks import NetworkInfo
from autotx.utils.ethereum.uniswap.swap import SUPPORTED_UNISWAP_V3_NETWORKS, build_swap_transaction
from gnosis.eth import EthereumNetworkNotSupported as ChainIdNotSupported

name = "swap-tokens"

system_message = lambda autotx: dedent(f"""
    You are an expert at buying and selling tokens. Assist the user (address: {autotx.manager.address}) in their task of swapping tokens.
    You use the tools available to assist the user in their tasks.
    Perform token swaps, manage liquidity, and query pool statistics on the Uniswap protocol
    An autonomous agent skilled in Ethereum blockchain interactions, specifically tailored for the Uniswap V3 protocol.
    Note a balance of a token is not required to perform a swap, if there is an earlier prepared transaction that will provide the token.
    IMPORTANT: Only one token amount should be provided. The other token amount will be calculated automatically.
    Examples:
    
    User: Sell 5 ETH and buy USDC
    Advisor reworded: Sell 5 ETH and buy USDC with address {autotx.manager.address}
    {{
        "token_to_sell": "5 ETH",
        "token_to_buy": "USDC"
    }}

    User: Sell ETH and buy 5 USDC
    Advisor reworded: Sell ETH and buy 5 USDC with address {autotx.manager.address}
    {{
        "token_to_sell": "ETH",
        "token_to_buy": "5 USDC"
    }}

    User: Swap ETH for 5 USDC, then swap that USDC for 5 UNI
    Advisor reworded: Swap ETH for 5 USDC, then swap 5 USDC for 6 UNI for user address {autotx.manager.address}
    {{
        "token_to_sell": "ETH",
        "token_to_buy": "5 USDC"
    }}
    and then
    {{
        "token_to_sell": "USDC",
        "token_to_buy": "6 UNI"
    }}

    Failed example:
    User: Swap ETH for 5 USDC, then swap that USDC for 5 UNI
    Advisor reworded: Swap ETH for 5 USDC, then swap 5 USDC for 6 UNI for user address {autotx.manager.address}
    {{
        "token_to_sell": "ETH",
        "token_to_buy": "5 USDC"
    }}
    and then
    {{
        "token_to_sell": "5 USDC",
        "token_to_buy": "6 UNI"
    }}
    Invalid input. Only one token amount should be provided. IMPORTANT: Take another look at the user's goal, and try again.
    Fix error:
    {{
        "token_to_sell": "USDC",
        "token_to_buy": "6 UNI"
    }}
    """
)

def get_tokens_address(token_in: str, token_out: str, network_info: NetworkInfo) -> tuple[str, str]:
    token_in = token_in.lower()
    token_out = token_out.lower()

    if not network_info.chain_id in SUPPORTED_UNISWAP_V3_NETWORKS:
        raise ChainIdNotSupported(
            f"Network {network_info.chain_id.name.lower()} not supported for swap"
        )

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
            is_exact_input = True if amount_symbol == token_symbol_to_sell else False

            (token_in_address, token_out_address) = get_tokens_address(
                token_in, token_out, autotx.network
            )

            swap_transactions = build_swap_transaction(
                autotx.manager.client,
                Decimal(exact_amount),
                token_in_address,
                token_out_address,
                autotx.manager.address.hex,
                is_exact_input,
            )
            autotx.transactions.extend(swap_transactions)

            token_in_amount = f"{exact_amount} " if is_exact_input else ""
            token_out_amount = f"{exact_amount} " if not is_exact_input else ""

            print(f"Prepared transaction: Buy {token_out_amount}{token_out} with {token_in_amount}{token_in}")

            return f"Transaction to buy {token_out_amount}{token_out} with {token_in_amount}{token_in} has been prepared"

        return run
    
class SwapTokensAgent(AutoTxAgent):
    name = name
    system_message = system_message
    tools = [
        SwapTool()
    ]
