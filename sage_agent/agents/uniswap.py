from textwrap import dedent
from crewai import Agent
from pydantic import ConfigDict, Field
from sage_agent.utils.ethereum.uniswap.swap import build_swap_transaction
from sage_agent.utils.agents_config import AgentConfig, agents_config
from sage_agent.utils.llm import open_ai_llm
from sage_agent.utils.ethereum.config import contracts_config
from web3.types import TxParams
from sage_agent.utils.user import get_configuration
from crewai_tools import BaseTool


# class SwapInput(BaseModel):
#     amount: int = Field(
#         description="Amount given by the user to trade. The function will take care of converting the amount to needed decimals"
#     )
#     token_in: str = Field(description="Symbol of token input")
#     token_out: str = Field(description="Symbol of token output")
#     exact_input: bool = Field(
#         description="If true, the amount is for `token_in`, else, amout is for `token_out`"
#     )


class ExecuteSwapTool(BaseTool):
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
            exact_input (str): True | False -> If True, the amount is for `token_in`, else, amout is for `token_out`.

        Returns:
            Array of encoded transaction(s)
        """
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)

    recipient: str | None = Field(None)

    def __init__(self, recipient: str):
        super().__init__()
        self.recipient = recipient

    def _run(
        self, amount: float, token_in: str, token_out: str, exact_input: str
    ) -> list[TxParams]:
        token_in = token_in.lower()
        token_out = token_out.lower()
        tokens = contracts_config["erc20"]
        exact_input = exact_input.lower() in ["true", "True"]

        token_in_address = tokens["weth"] if token_in == "eth" else tokens[token_in]
        token_out_address = tokens["weth"] if token_out == "eth" else tokens[token_out]

        (_, _, client) = get_configuration()

        swap_transactions = build_swap_transaction(
            client,
            amount,
            token_in_address,
            token_out_address,
            self.recipient,
            exact_input,
        )

        return swap_transactions


class UniswapAgent(Agent):
    name: str

    def __init__(self, recipient: str):
        name = "uniswap"
        config: AgentConfig = agents_config[name].model_dump()
        super().__init__(
            **config,
            tools=[ExecuteSwapTool(recipient)],
            llm=open_ai_llm,
            verbose=True,
            allow_delegation=False,
            name=name
        )
