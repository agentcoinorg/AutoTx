from typing import Any
from langchain_core.tools import tool
from crewai import Agent
from pydantic import BaseModel, Field
from sage_agent.agents.safe import Transaction, convert_tx_params_to_transaction
from sage_agent.swap import build_swap_transaction
from sage_agent.utils.agents_config import AgentConfig, agents_config
from sage_agent.utils.llm import open_ai_llm
from sage_agent.utils.ethereum.config import contracts_config
from web3.types import TxParams

from sage_agent.utils.user import get_configuration


class SwapInput(BaseModel):
    amount: int = Field(
        description="Amount given by the user to trade. The function will take care of converting the amount to needed decimals"
    )
    token_in: str = Field(description="Symbol of token input")
    token_out: str = Field(description="Symbol of token output")
    exact_input: bool = Field(
        description="If true, the amount is for `token_in`, else, amout is for `token_out`"
    )


@tool("Build needed transactions to execute swap")
def build_swap(
    amount: int, token_in: str, token_out: str, exact_input: str
) -> Transaction:
    """
    Encodes approve, if necessary and swap transactions. The function will only add the approve transaction
    if the address does not have enough allowance

    Args:
        amount (int): Amount given by the user to trade. The function will take care of converting the amount
        to needed decimals.
        token_in (str): Symbol of token input.
        token_out (str): Symbol of token output.
        exact_input (str): True | False -> If True, the amount is for `token_in`, else, amout is for `token_out`.

    Returns:
        Array of encoded transaction(s)
    """
    # print(amount)
    # print(token_in)
    # print(token_out)
    # print(exact_input)

    # amount = args.amount
    # token_in = args.token_in.lower()
    # token_out = args.token_out.lower()
    # exact_input = args.exact_input

    # # print(token_in)
    # # print(token_out)

    # print(amount)
    token_in = token_in.lower()
    token_out = token_out.lower()
    tokens = contracts_config["erc20"]
    exact_input = exact_input.lower() in ["true", "True"]

    token_in_address = tokens["weth"] if token_in == "eth" else tokens[token_in]
    token_out_address = tokens["weth"] if token_out == "eth" else tokens[token_out]

    # print(available_tokens)
    # print(token_in)
    # print(token_out)
    # # if token_in != "eth" and token_in not in available_tokens:
    # #     print("wrong token for token in!")

    # # if token_out != "eth" and token_out not in available_tokens:
    # #     print("wrong token for token out!")
    (_, _, client) = get_configuration()
    swap_transactions = build_swap_transaction(
        client,
        amount,
        token_in_address,
        token_out_address,
        "0x65D6359706D7a27e674a2C2D33b67cF6FB496Cd7",
        exact_input,
    )

    return [convert_tx_params_to_transaction(tx) for tx in swap_transactions]


default_tools = [build_swap]


class UniswapAgent(Agent):
    name: str

    def __init__(self):
        name = "uniswap"
        config: AgentConfig = agents_config[name].model_dump()
        super().__init__(
            **config,
            tools=[build_swap],
            llm=open_ai_llm,
            verbose=True,
            allow_delegation=False,
            name=name
        )
