from typing import Optional
from langchain_core.tools import Tool, tool
from crewai import Agent
from sage_agent.utils.agents_config import AgentConfig, agents_config
from sage_agent.utils.llm import open_ai_llm
import json


@tool("Encode method and arguments to interact with ERC20 contract")
def encode(name, arguments):
    """
    Encodes method and arguments into calldata. Allowing to interact
    with the ERC20 using the `data` attribute from transaction

    :param name: str, name of the function to encode
    :param arguments: str, value of arguments to execute function

    :result calldata: str, calldata to execute function
    """
    return "0xSUPER_COOL_CALL_DATA"


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
    encode,
    get_balance,
    get_information,
]


class Erc20Agent(Agent):
    def __init__(self) -> Agent:
        config: AgentConfig = agents_config["erc20"].model_dump()
        super().__init__(
            **config,
            tools=default_tools,
            llm=open_ai_llm,
            verbose=True,
            allow_delegation=False,
        )
