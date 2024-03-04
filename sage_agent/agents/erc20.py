from langchain_core.tools import tool
from crewai import Agent
from sage_agent.utils.agents_config import AgentConfig, agents_config
from sage_agent.utils.ethereum import build_approve_erc20, build_transfer_erc20, get_erc20_balance
from sage_agent.utils.ethereum import load_w3
from sage_agent.utils.ethereum.get_erc20_info import get_erc20_info
from sage_agent.utils.llm import open_ai_llm
import json


@tool("Encode transfer function")
def encode_transfer_function(amount: str, reciever: str, token_address: str):
    """
    Encodes token transfer function calldata with amount in decimals for given token

    Args:
        amount (int): The amount in decimals of token.
        reciever (str): The address of reciever
        token_address (str): The address of the token to interact with
    Returns:
        str: Transaction data of the transfer function.
    """
    tx = build_transfer_erc20(load_w3(), token_address, reciever, int(amount))

    return json.dumps(tx)


@tool("Encodes approve function")
def encode_approve_function(amount: int, spender: str, token_address: str) -> str:
    """
    Encodes token approval function calldata with amount in decimals for given token

    Args:
        amount (int): The amount in decimals of token.
        spender (str): The address of the spender
        token_address (str): The address of the token to interact with
    Returns:
        str: Transaction data of the approve function.
    """

    tx = build_approve_erc20(load_w3(), spender, token_address, amount)

    return json.dumps(tx)


@tool("Check owner balance in ERC20 token")
def get_balance(address, owner):
    """
    Check balance of given owner in ERC20 contract

    :param address: str, address of erc20 contract
    :param owner: str, address of owner of tokens

    :result balance: int, the balance of owner in erc20 contract
    """

    return get_erc20_balance(load_w3(), address, owner)


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
    name, symbol, decimals = get_erc20_info(load_w3(), address)

    token = {"decimals": decimals, "name": name, "symbol": symbol}
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
