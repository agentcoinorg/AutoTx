from langchain_core.tools import tool
from crewai import Agent
from pydantic import BaseModel, Field
from sage_agent.utils.agents_config import AgentConfig, agents_config
from sage_agent.utils.llm import open_ai_llm
import json


@tool("Encode transfer function")
def encode_transfer_function(name, arguments):
    """
    Encodes token transfer function calldata with amount in decimals for given token

    Args:
        amount (int): The amount in decimals of token.
        token_address (str): The address of the token
    Returns:
        str: Calldata of the transfer function.
    """
    return "0x_TRANSFER_CALLDATA"

@tool("Encodes approve function")
def encode_approve_function(amount: int, token_address: str) -> str:
    """
    Encodes token approval function calldata with amount in decimals for given token

    Args:
        amount (int): The amount in decimals of token.
        token_address(str): The address of the token
    Returns:
        str: Calldata of the approve function.
    """

    return "0x_APPROVE_CALLDATA"


@tool("Check owner balance in ERC20 token")
def get_balance(address, owner):
    """
    Check balance of given owner in ERC20 contract

    :param address: str, address of erc20 contract
    :param owner: str, address of owner of tokens

    :result balance: int, the balance of owner in erc20 contract
    """
    return "12455"


@tool("Get decimals, name and symbol for an ERC")
def get_information(address):
    """
    Gets decimals, name and symbol from given address of ERC20

    :param address: str, address of erc20 token contract

    :result information: str, a string representation of the token information

    example information:
    {
        "decimals": 6,
        "name": "COOL TOKEN",
        "symbol": "$$$"
    }
    """
    token = {"decimals": 6, "name": "COOL TOKEN", "symbol": "$$$"}
    return json.dumps(token)


default_tools = [
    encode_approve_function,
    encode_transfer_function,
    get_balance,
    get_information,
]


class Erc20Agent(Agent):
    name: str

    def __init__(self):
        name = "erc20"
        config: AgentConfig = agents_config[name].model_dump()
        super().__init__(
            **config,
            tools=default_tools,
            llm=open_ai_llm,
            verbose=True,
            allow_delegation=False,
            name=name
        )
