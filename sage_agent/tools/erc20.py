import json
from langchain.tools import tool

class Erc20Tools:
    @tool("Encode send ERC20 transaction")
    def encode(name, arguments):
        """
        :param name: str, name of the function to encode
        :param arguments: str, value of arguments to execute function

        :result encodedFunction: str, calldata to execute function
        """
        return "0xSUPER_COOL_CALL_DATA"
    
    @tool("Check owner balance in ERC20 token")
    def get_balance(address, owner):
        """
        :param address: str, address of erc20 contract
        :param owner: str, address of owner of tokens

        :result balance: int, the balance of owner in erc20 contract
        """
        return "12455"
    
    @tool("Get decimals, name and symbol for an ERC")
    def get_information(address):
        """
        :param address: str, address of erc20 token contract

        :result information: str, a string representation of the token information

        example information:
        {
            "decimals": 6,
            "name": "COOL TOKEN",
            "symbol": "$$$"
        }
        """
        token = {
            "decimals": 6,
            "name": "COOL TOKEN",
            "symbol": "$$$"
        }
        return json.dumps(token)