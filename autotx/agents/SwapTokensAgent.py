from decimal import Decimal
from textwrap import dedent
from typing import Annotated, Callable
from autotx import models
from autotx.AutoTx import AutoTx
from autotx.autotx_agent import AutoTxAgent
from autotx.autotx_tool import AutoTxTool
from autotx.utils.ethereum.eth_address import ETHAddress
from autotx.utils.ethereum.lifi.swap import SUPPORTED_NETWORKS_BY_LIFI, build_swap_transaction
from autotx.utils.ethereum.networks import NetworkInfo
from gnosis.eth import EthereumNetworkNotSupported as ChainIdNotSupported

name = "swap-tokens"

system_message = lambda autotx: dedent(f"""
    You are an expert at buying and selling tokens. Assist the user in their task of swapping tokens.
    ONLY focus on the buy and sell (swap) aspect of the user's goal and let other agents handle other tasks.
    You use the tools available to assist the user in their tasks.
    Note a balance of a token is not required to perform a swap, if there is an earlier prepared transaction that will provide the token.
    Below are examples, NOTE these are only examples and in practice you need to call the prepare_bulk_swap_transactions tool with the correct arguments.
    NEVER ask the user questions.
    Example 1:
    User: Send 0.1 ETH to vitalik.eth and then swap ETH to 5 USDC
    ...
    Other agent messages
    ...
    Call prepare_bulk_swap_transactions: "ETH to 5 USDC"

    Example 1:
    User: Buy 10 USDC with ETH and then buy UNI with 5 USDC
    Call prepare_bulk_swap_transactions: "ETH to 10 USDC\n5 USDC to UNI"

    Example 2:
    User: Buy UNI, WBTC, USDC and SHIB with 0.92 ETH
    Call prepare_bulk_swap_transactions: "0.23 ETH to UNI\n0.23 ETH to WBTC\n0.23 ETH to USDC\n0.23 ETH to SHIB"

    Example 3:
    User: Swap ETH to 5 USDC, then swap that USDC for 6 UNI
    Call prepare_bulk_swap_transactions: "ETH to 5 USDC\nUSDC to 6 UNI"
                                       
    Example 4:
    User: Buy 2 ETH worth of WBTC and then send 1 WBTC to 0x123..456
    Call prepare_bulk_swap_transactions: "2 ETH to WBTC"
                                       
    Example of a bad input:
    User: Swap ETH to 1 UNI, then swap UNI to 4 USDC
    Call prepare_bulk_swap_transactions: "ETH to 1 UNI\n1 UNI to 4 USDC"
    Prepared transaction: Swap 1.0407386618866115 ETH for at least 1 WBTC
    Invalid input: "1 UNI to 4 USDC". Only one token amount should be provided. IMPORTANT: Take another look at the user's goal, and try again.
    In the above example, you recover with:
    Call prepare_bulk_swap_transactions: "UNI to 4 USDC"
                                       
    Above are examples, NOTE these are only examples and in practice you need to call the prepare_bulk_swap_transactions tool with the correct arguments.
    Take extra care in ensuring you have to right amount next to the token symbol. NEVER use more than one amount per swap, the other amount will be calculated for you.
    The swaps are NOT NECESSARILY correlated, focus on the exact amounts the user wants to buy or sell (leave the other amounts to be calculated for you).
    You rely on the other agents to provide the token to buy or sell. Never make up a token. Unless explicitly given the name of the token, ask the 'research-tokens' agent to first search for the token.
    Only call tools, do not respond with JSON.
    """
)

description = dedent(
    f"""
    {name} is an AI assistant that's an expert at buying and selling tokens.
    The agent can prepare transactions to swap tokens.
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

class InvalidInput(Exception):
    pass

def swap(autotx: AutoTx, token_to_sell: str, token_to_buy: str) -> list[models.Transaction]:
    sell_parts = token_to_sell.split(" ")
    buy_parts = token_to_buy.split(" ")

    if not autotx.network.chain_id in SUPPORTED_NETWORKS_BY_LIFI:
        raise ChainIdNotSupported(
            f"Network {autotx.network.chain_id.name.lower()} not supported for swap"
        )

    if len(sell_parts) == 2 and len(buy_parts) == 2:
        sell_amount = Decimal(sell_parts[0])
        buy_amount = Decimal(buy_parts[0])
        sell_token = sell_parts[1]
        buy_token = buy_parts[1]

        raise InvalidInput(f"Invalid input: \"{token_to_sell} to {token_to_buy}\". Only one token amount should be provided. Choose between '{sell_amount} {sell_token} to {buy_token}' or '{sell_token} to {buy_amount} {buy_token}'.")
    
    if len(sell_parts) < 2 and len(buy_parts) < 2:
        raise InvalidInput(f"Invalid input: \"{token_to_sell} to {token_to_buy}\". Token amount is missing. Only one token amount should be provided.")

    if len(sell_parts) > 2 or len(buy_parts) > 2:
        raise InvalidInput(f"Invalid input: \"{token_to_sell} to {token_to_buy}\". Too many token amounts or token symbols provided. Only one token amount and two token symbols should be provided per line.")

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
        autotx.web3,
        Decimal(exact_amount),
        ETHAddress(token_in_address),
        ETHAddress(token_out_address),
        autotx.wallet.address,
        is_exact_input,
        autotx.network.chain_id
    )
    autotx.add_transactions(swap_transactions)

    return swap_transactions

class BulkSwapTool(AutoTxTool):
    name: str = "prepare_bulk_swap_transactions"
    description: str = dedent(
        """
        Prepares a batch of buy transactions for given amounts in decimals for given tokens.
        """
    )

    def build_tool(self, autotx: AutoTx) -> Callable[[str], str]:
        def run(
            tokens: Annotated[
                str, 
                """
                Tokens and amounts to swap. ONLY one amount should be provided next to the token symbol PER line.
                E.g:
                10 USDC to ETH
                UNI to 3.3 WBTC
                1.5 WBTC to USDC
                """
            ],
        ) -> str:
            swaps = tokens.split("\n")
            all_txs = []
            all_errors: list[Exception] = []

            for swap_str in swaps:
                (token_to_sell, token_to_buy) = swap_str.strip().split(" to ")
                try:
                    txs = swap(autotx, token_to_sell, token_to_buy)
                    all_txs.extend(txs)
                except InvalidInput as e:
                    all_errors.append(e)
                except Exception as e:
                    all_errors.append(Exception(f"Error: {e} for swap \"{token_to_sell} to {token_to_buy}\""))


            summary = "".join(
                f"Prepared transaction: {swap_transaction.summary}\n"
                for swap_transaction in all_txs
            )

            if all_errors:
                summary += "\n".join(str(e) for e in all_errors)
                if len(all_txs) > 0:
                    summary += f"\n{len(all_errors)} errors occurred. {len(all_txs)} transactions were prepared. There is no need to re-run the transactions that were prepared."
                else:
                    summary += f"\n{len(all_errors)} errors occurred."

            total_summary = ("\n" + " " * 16).join(
                [
                    f"{i + 1}. {tx.summary}"
                    for i, tx in enumerate(autotx.transactions)
                ]
            )

            autotx.notify_user(summary)

            return dedent(
                f"""
                {summary}
                Total prepared transactions so far:
                {total_summary}
                """
            )

        return run

class SwapTokensAgent(AutoTxAgent):
    name = name
    system_message = system_message
    description = description
    tools = [
        BulkSwapTool()
    ]
