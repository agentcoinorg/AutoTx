from textwrap import dedent
from crewai import Agent
from pydantic import ConfigDict, Field
from autotx.utils.ethereum.uniswap.swap import build_swap_transaction
from autotx.utils.agents_config import AgentConfig, agents_config
from autotx.utils.llm import open_ai_llm
from autotx.utils.ethereum.config import contracts_config
from autotx.AutoTx import transactions
from web3.types import TxParams
from crewai_tools import BaseTool
from gnosis.eth import EthereumClient


class ExecuteSwapTool(BaseTool):
    name: str = "Build needed transactions to execute swap"
    description: str = dedent(
        """
        Encodes approve, if necessary and swap transactions. The function will only add the approve transaction
        if the address does not have enough allowance

        Args:
            amount (str): Amount given by the user to trade. The function will take care of converting the amount
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
    model_config = ConfigDict(arbitrary_types_allowed=True)
    recipient: str | None = Field(None)
    client: EthereumClient | None = Field(None)

    def __init__(self, client: EthereumClient, recipient: str):
        super().__init__()
        self.client = client
        self.recipient = recipient

    def _run(
        self, amount: str, token_in: str, token_out: str, exact_input: str
    ) -> list[TxParams]:
        token_in = token_in.lower()
        token_out = token_out.lower()
        tokens = contracts_config["erc20"]
        is_exact_input = exact_input in ["true", "True"]

        # TODO: Handle when `token_in` or `token_out` are not in the `tokens` list
        token_in_address = tokens["weth"] if token_in == "eth" else tokens[token_in]
        token_out_address = tokens["weth"] if token_out == "eth" else tokens[token_out]

        swap_transactions = build_swap_transaction(
            self.client,
            float(amount),
            token_in_address,
            token_out_address,
            self.recipient,
            is_exact_input,
        )

        transactions.extend(swap_transactions)

        if is_exact_input:
            return f"Transaction to sell {amount} {token_in} for {token_out} has been prepared"
        else:
            return f"Transaction to buy {amount} {token_out} with {token_in} has been prepared"


class UniswapAgent(Agent):
    name: str

    def __init__(self, client: EthereumClient, recipient: str):
        name = "uniswap"
        config: AgentConfig = agents_config[name].model_dump()
        super().__init__(
            **config,
            tools=[ExecuteSwapTool(client, recipient)],
            llm=open_ai_llm,
            verbose=True,
            allow_delegation=False,
            name=name,
        )
