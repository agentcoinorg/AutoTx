from langchain_core.tools import tool
from crewai import Agent
from pydantic import Field
from web3 import Web3
from sage_agent.utils.agents_config import AgentConfig, agents_config
from sage_agent.utils.ethereum import build_approve_erc20, build_transfer_erc20, get_erc20_balance
from sage_agent.utils.ethereum import load_w3
from sage_agent.utils.ethereum.get_erc20_info import get_erc20_info
from sage_agent.utils.llm import open_ai_llm
import json
from crewai_tools import BaseTool
from sage_agent.utils.ethereum.config import contracts_config
from sage_agent.sage import transactions

@tool("Prepare transfer transaction")
def prepare_transfer_transaction(amount: float, reciever: str, token: str):
    """
    Prepares a transfer transaction for given amount in decimals for given token

    Args:
        amount (float): Amount given by the user to transfer. The function will take
        care of converting the amount to needed decimals.
        reciever (str): The address of reciever
        token (str): Symbol of token to transfer
    Returns:
        Transaction object with filled data to execute transfer
    """
    tokens = contracts_config["erc20"]
    token_address = tokens[token.lower()]
    tx = build_transfer_erc20(load_w3(), token_address, reciever, amount)

    transactions.append(tx)

    return tx

@tool("Parse token units")
def parse_token_units(amount: int, decimals: int):
    """
    Parses the amount of token with unit digits

    Args:
        amount (int): The amount of the token
        decimals (int): The decimals of the token
    Returns:
        int: The amount of token parsed with unit digits
    """
    
    return amount * 10 ** decimals

@tool("Prepare approve transaction")
def prepare_approve_transaction(amount: int, spender: str, token_address: str) -> str:
    """
    Prepares an approve transaction for given amount of token to spender

    Args:
        amount (int): The amount in decimals of token.
        spender (str): The address of the spender
        token_address (str): The address of the token to interact with
    Returns:
        str: The JSON representation of the transaction
    """

    tx = build_approve_erc20(load_w3(), token_address, spender, amount)

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
    name, symbol, decimals = get_erc20_info(load_w3(), Web3.to_checksum_address(address))

    token = {"decimals": decimals, "name": name, "symbol": symbol}
    return json.dumps(token)

class GetTokenAddressTool(BaseTool):
    name: str = "Get ERC20 token address"
    description: str = "Get the address of the ERC20 token with the given symbol"
    token_addresses: list[str] = Field([])

    def __init__(self, token_addresses: list[str]):
        super().__init__()
        self.token_addresses = token_addresses

    def _run(self, symbol: str) -> str:
        for address in self.token_addresses:
            token = json.loads(get_information(address))
            if token["symbol"] == symbol.lower():
                return address
        
        raise ValueError(f"Token with symbol {symbol} not found")

class Erc20Agent(Agent):
    name: str

    def __init__(self):
        name = "erc20"
        config: AgentConfig = agents_config[name].model_dump()
        super().__init__(
            **config,
            tools=[
                prepare_transfer_transaction,
                # prepare_approve_transaction,
                # get_balance,
                # get_information,
                # parse_token_units,
                # GetTokenAddressTool(token_addresses),
            ],
            llm=open_ai_llm,
            verbose=True,
            allow_delegation=False,
            name=name
        )