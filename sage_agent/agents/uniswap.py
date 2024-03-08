from langchain_core.tools import tool
from crewai import Agent
from sage_agent.utils.agents_config import AgentConfig, agents_config
from sage_agent.utils.llm import open_ai_llm

@tool(
    "Queries the Uniswap pool for a given token pair to obtain necessary parameters for a swap."
)
def query_pools(token_in_address: str, token_out_address: str, fee: int) -> dict:
    """
    Queries the Uniswap pool for a given token pair to obtain necessary parameters for a swap.

    Args:
        token_in_address (str): The address of the input token contract.
        token_out_address (str): The address of the output token contract.
        fee (int): The fee tier of the pool to query.

    Returns:
        dict: A dictionary containing details about the pool, such as the pool address and any other necessary swap parameters.

    Description:
        Queries the specified Uniswap pool for the given token pair (input and output tokens) at the specified fee tier. It returns a dictionary with the pool's address and other relevant information that might be needed for calculating the swap
    """

    return {"pool_address": "0x_POOL_ADDRESS", "metadata": {}}


@tool(
    "Encodes a swap transaction for a specified amount of input tokens to output tokens using a Uniswap pool."
)
def encode_swap(
    pool_address: str,
    amount_in: int,
    slippage_tolerance: float,
    recipient_address: str,
    deadline: int,
) -> str:
    """
    Encodes a swap transaction for a specified amount of input tokens to output tokens using a Uniswap pool.

    Args:
        pool_address (str): The address of the Uniswap pool to interact with.
        amount_in (int): The amount of input tokens to swap.
        slippage_tolerance (float): The maximum acceptable slippage for the swap, in percentage terms.
        recipient_address (str): The address of the recipient for the output tokens.
        deadline (int): The latest timestamp (in Unix time) by which the transaction must be confirmed.

    Returns:
        str: The encoded data for the swap transaction, ready to be signed and sent to the Ethereum network.

    Description:
        This tool takes the necessary parameters for performing a token swap on Uniswap and encodes them into a transaction. It requires the address of the Uniswap pool, the amount of tokens to be swapped, and details such as slippage tolerance and transaction deadline. The function returns the encoded transaction data.
    """

    return "0x_SWAP_CALLDATA"

class UniswapAgent(Agent):
    name: str

    def __init__(self):
        name = "uniswap"
        config: AgentConfig = agents_config[name].model_dump()
        super().__init__(
            **config,
            tools=[query_pools, encode_swap],
            llm=open_ai_llm,
            verbose=True,
            allow_delegation=False,
            name=name
        )
