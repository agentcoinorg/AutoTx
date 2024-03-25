from textwrap import dedent
from typing import Callable
from crewai import Agent
from pydantic import Field
from autotx.AutoTx import AutoTx
from autotx.auto_tx_agent import AutoTxAgent
from autotx.auto_tx_tool import AutoTxTool
from autotx.utils.ethereum.uniswap.swap import build_swap_transaction
from gnosis.eth import EthereumClient

class ExecuteSwapTool(AutoTxTool):
    name: str = "Build needed transactions to execute swap"
    description: str = dedent(
        """
        Encodes approve, if necessary and swap transactions. The function will only add the approve transaction
        if the address does not have enough allowance

        Args:
            amount (float): Amount given by the user to trade. The function will take care of converting the amount
            to needed decimals.
            token_in (str): Symbol of token input.
            token_out (str): Symbol of token output.
            exact_input (str): A flag indicating the direction of the trade with respect to the amount specified:
                - If True, the amount refers to the exact quantity of `token_in` that the user wishes to swap.
                - If False, the amount refers to the exact quantity of `token_out` that the user wishes to receive.
                This distinction is crucial for determining how the swap transaction is structured, particularly
                in specifying the limits of token exchange rates and the adjustment of transaction parameters.
        """
    )
    recipient: str | None = Field(None)
    client: EthereumClient | None = Field(None)

    def __init__(self, autotx: AutoTx, client: EthereumClient, recipient: str):
        super().__init__(autotx)
        self.client = client
        self.recipient = recipient

    def _run(
        self, amount: float, token_in: str, token_out: str, exact_input: str
    ) -> str:
        token_in = token_in.lower()
        token_out = token_out.lower()
        tokens = self.autotx.network.tokens
        is_exact_input = exact_input in ["true", "True"]

        # TODO: Handle when `token_in` or `token_out` are not in the `tokens` list
        token_in_address = tokens["weth"] if token_in == "eth" else tokens[token_in]
        token_out_address = tokens["weth"] if token_out == "eth" else tokens[token_out]

        swap_transactions = build_swap_transaction(
            self.client,
            amount,
            token_in_address,
            token_out_address,
            self.recipient,
            is_exact_input,
        )
        self.autotx.transactions.extend(swap_transactions)

        if is_exact_input:
            return f"Transaction to sell {amount} {token_in} for {token_out} has been prepared"
        else:
            return f"Transaction to buy {amount} {token_out} with {token_in} has been prepared"

class SwapTokensAgent(AutoTxAgent):
    def __init__(self, autotx: AutoTx, client: EthereumClient, recipient: str):
        super().__init__(
            name="swap-tokens",
            role="Expert in swapping tokens",
            goal="Perform token swaps, manage liquidity, and query pool statistics on the Uniswap protocol",
            backstory="An autonomous agent skilled in Ethereum blockchain interactions, specifically tailored for the Uniswap V3 protocol.",
            tools=[ExecuteSwapTool(autotx, client, recipient)],
        )

def build_agent_factory(client: EthereumClient, recipient: str) -> Callable[[AutoTx], Agent]:
    def agent_factory(autotx: AutoTx) -> SwapTokensAgent:
        return SwapTokensAgent(autotx, client, recipient)
    return agent_factory
